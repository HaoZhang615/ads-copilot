import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter, ValidationError

from app.backend.models.session_state import SessionState
from app.backend.models.ws_messages import (
    AgentTextMessage,
    AudioMessage,
    ControlMessage,
    ErrorMessage,
    IncomingMessage,
    StateMessage,
    TextMessage,
    TranscriptMessage,
    TtsAudioMessage,
)

from app.backend.services.session_manager import Session, session_manager

logger = logging.getLogger(__name__)

router = APIRouter()

_incoming_adapter = TypeAdapter(IncomingMessage)


async def _send_msg(ws: WebSocket, data: dict[str, Any]) -> None:
    try:
        await ws.send_json(data)
    except Exception:
        logger.debug("Failed to send WS message", exc_info=True)


async def _set_state(ws: WebSocket, session: Session, state: SessionState) -> None:
    session.state = state
    await _send_msg(ws, StateMessage(state=state).model_dump())


async def _handle_audio(ws: WebSocket, session: Session, msg: AudioMessage) -> None:
    try:
        await session.voicelive.send_audio(msg.data)
    except Exception:
        await _send_msg(ws, ErrorMessage(message="Failed to send audio to VoiceLive").model_dump())


async def _process_agent_response(
    ws: WebSocket,
    session: Session,
    text: str,
    agent_lock: asyncio.Lock,
) -> None:
    """Send text to the Copilot agent and stream the response back.

    Runs as a background task so the WS receive loop is never blocked.
    Uses agent_lock to serialise concurrent agent calls (e.g. rapid user
    messages or voice transcriptions arriving while a previous turn is
    still streaming).
    """
    async with agent_lock:
        await _set_state(ws, session, SessionState.THINKING)
        session.turn_count += 1
        session.conversation_history.append({"role": "user", "content": text})

        full_response: list[str] = []
        try:
            async for chunk in session.copilot.send_message(text):
                full_response.append(chunk)
                await _send_msg(ws, AgentTextMessage(text=chunk, is_final=False).model_dump())

            final_text = "".join(full_response)
            if final_text:
                await _send_msg(ws, AgentTextMessage(text=final_text, is_final=True).model_dump())
            session.conversation_history.append({"role": "assistant", "content": final_text})

            # Request TTS for the response (only if VoiceLive is connected
            # and there is actual text).
            if final_text:
                await _set_state(ws, session, SessionState.SPEAKING)
                logger.info("TTS: sending full response to VoiceLive (%d chars)", len(final_text))
                try:
                    await session.voicelive.send_tts_request(final_text)
                except Exception:
                    logger.warning("TTS request failed", exc_info=True)

        except Exception:
            logger.exception("Error processing agent response")
            await _send_msg(ws, ErrorMessage(message="Error processing your message").model_dump())
        finally:
            await _set_state(ws, session, SessionState.IDLE)


async def _handle_text(
    ws: WebSocket,
    session: Session,
    msg: TextMessage,
    agent_lock: asyncio.Lock,
) -> asyncio.Task[None]:
    """Kick off agent processing in a background task (non-blocking)."""
    return asyncio.create_task(
        _process_agent_response(ws, session, msg.content, agent_lock),
        name="agent-text",
    )


async def _handle_control(ws: WebSocket, session: Session, msg: ControlMessage) -> None:
    if msg.action == "start_session":
        await _send_msg(ws, StateMessage(state=session.state).model_dump())

    elif msg.action == "end_session":
        await session_manager.cleanup_session(session.session_id)
        await _send_msg(ws, StateMessage(state=SessionState.IDLE).model_dump())

    elif msg.action == "start_listening":
        await _set_state(ws, session, SessionState.LISTENING)

    elif msg.action == "stop_listening":
        await _set_state(ws, session, SessionState.IDLE)


async def _voicelive_listener(
    ws: WebSocket,
    session: Session,
    agent_lock: asyncio.Lock,
) -> None:
    """Listen for VoiceLive events and dispatch agent calls as background tasks."""
    agent_tasks: list[asyncio.Task[None]] = []

    try:
        async for event in session.voicelive.receive_events():
            event_type = event.get("type", "")

            if event_type == "conversation.item.input_audio_transcription.completed":
                text = event.get("transcript", "")
                if text:
                    await _send_msg(ws, TranscriptMessage(text=text, is_final=True).model_dump())

                    # Spawn agent processing in background (non-blocking)
                    task = asyncio.create_task(
                        _process_agent_response(ws, session, text, agent_lock),
                        name="agent-voice",
                    )
                    agent_tasks.append(task)

            elif event_type == "conversation.item.input_audio_transcription.delta":
                text = event.get("transcript", "") or event.get("delta", "")
                if text:
                    await _send_msg(ws, TranscriptMessage(text=text, is_final=False).model_dump())

            elif event_type == "response.audio.delta":
                audio_data = event.get("delta", "")
                if audio_data:
                    logger.debug("TTS audio.delta received (%d chars)", len(audio_data))
                    await _send_msg(ws, TtsAudioMessage(data=audio_data).model_dump())

            elif event_type == "response.audio.done":
                await _set_state(ws, session, SessionState.IDLE)

            elif event_type == "error":
                error_msg = event.get("error", {}).get("message", "VoiceLive error")
                await _send_msg(ws, ErrorMessage(message=error_msg).model_dump())

    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("VoiceLive listener error")
    finally:
        # Clean up any outstanding agent tasks
        for task in agent_tasks:
            if not task.done():
                task.cancel()
        for task in agent_tasks:
            if not task.done():
                try:
                    await task
                except asyncio.CancelledError:
                    pass


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    session: Session | None = None
    voicelive_task: asyncio.Task[None] | None = None
    agent_tasks: list[asyncio.Task[None]] = []
    # Serialises agent calls so concurrent text/voice messages don't
    # interleave their streaming responses.
    agent_lock = asyncio.Lock()

    try:
        user_id = websocket.query_params.get("user_id", "anonymous")
        session = await session_manager.create_session(user_id)

        await _send_msg(websocket, {
            "type": "session_created",
            "session_id": session.session_id,
        })
        await _send_msg(websocket, StateMessage(state=session.state).model_dump())

        voicelive_task = asyncio.create_task(
            _voicelive_listener(websocket, session, agent_lock),
        )

        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
                msg = _incoming_adapter.validate_python(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                await _send_msg(websocket, ErrorMessage(message=f"Invalid message: {exc}").model_dump())
                continue

            if isinstance(msg, AudioMessage):
                await _handle_audio(websocket, session, msg)
            elif isinstance(msg, TextMessage):
                # Non-blocking: agent runs in background task
                task = await _handle_text(websocket, session, msg, agent_lock)
                agent_tasks.append(task)
            elif isinstance(msg, ControlMessage):
                await _handle_control(websocket, session, msg)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception:
        logger.exception("WebSocket error")
    finally:
        # Cancel agent tasks
        for task in agent_tasks:
            if not task.done():
                task.cancel()
        for task in agent_tasks:
            if not task.done():
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if voicelive_task and not voicelive_task.done():
            voicelive_task.cancel()
            try:
                await voicelive_task
            except asyncio.CancelledError:
                pass
        if session:
            await session_manager.cleanup_session(session.session_id)
