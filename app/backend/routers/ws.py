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
from app.backend.services.audio_utils import detect_sentence_boundaries
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


async def _handle_text(ws: WebSocket, session: Session, msg: TextMessage) -> None:
    await _set_state(ws, session, SessionState.THINKING)
    session.turn_count += 1
    session.conversation_history.append({"role": "user", "content": msg.content})

    full_response: list[str] = []
    try:
        async for chunk in session.copilot.send_message(msg.content):
            full_response.append(chunk)
            await _send_msg(ws, AgentTextMessage(text=chunk, is_final=False).model_dump())

        final_text = "".join(full_response)
        await _send_msg(ws, AgentTextMessage(text=final_text, is_final=True).model_dump())
        session.conversation_history.append({"role": "assistant", "content": final_text})

        await _set_state(ws, session, SessionState.SPEAKING)
        sentences = detect_sentence_boundaries(final_text)
        for sentence in sentences:
            try:
                await session.voicelive.send_tts_request(sentence)
            except Exception:
                logger.warning("TTS request failed for sentence", exc_info=True)

    except Exception:
        logger.exception("Error processing text message")
        await _send_msg(ws, ErrorMessage(message="Error processing your message").model_dump())
    finally:
        await _set_state(ws, session, SessionState.IDLE)


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


async def _voicelive_listener(ws: WebSocket, session: Session) -> None:
    try:
        async for event in session.voicelive.receive_events():
            event_type = event.get("type", "")

            if event_type == "conversation.item.input_audio_transcription.completed":
                text = event.get("transcript", "")
                if text:
                    await _send_msg(ws, TranscriptMessage(text=text, is_final=True).model_dump())

                    await _set_state(ws, session, SessionState.THINKING)
                    session.turn_count += 1
                    session.conversation_history.append({"role": "user", "content": text})

                    full_response: list[str] = []
                    async for chunk in session.copilot.send_message(text):
                        full_response.append(chunk)
                        await _send_msg(ws, AgentTextMessage(text=chunk, is_final=False).model_dump())

                    final_text = "".join(full_response)
                    await _send_msg(ws, AgentTextMessage(text=final_text, is_final=True).model_dump())
                    session.conversation_history.append({"role": "assistant", "content": final_text})

                    await _set_state(ws, session, SessionState.SPEAKING)
                    sentences = detect_sentence_boundaries(final_text)
                    for sentence in sentences:
                        try:
                            await session.voicelive.send_tts_request(sentence)
                        except Exception:
                            logger.warning("TTS request failed", exc_info=True)

            elif event_type == "conversation.item.input_audio_transcription.delta":
                text = event.get("transcript", "") or event.get("delta", "")
                if text:
                    await _send_msg(ws, TranscriptMessage(text=text, is_final=False).model_dump())

            elif event_type == "response.audio.delta":
                audio_data = event.get("delta", "")
                if audio_data:
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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    session: Session | None = None
    voicelive_task: asyncio.Task[None] | None = None

    try:
        user_id = websocket.query_params.get("user_id", "anonymous")
        session = await session_manager.create_session(user_id)

        await _send_msg(websocket, {
            "type": "session_created",
            "session_id": session.session_id,
        })
        await _send_msg(websocket, StateMessage(state=session.state).model_dump())

        voicelive_task = asyncio.create_task(_voicelive_listener(websocket, session))

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
                await _handle_text(websocket, session, msg)
            elif isinstance(msg, ControlMessage):
                await _handle_control(websocket, session, msg)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception:
        logger.exception("WebSocket error")
    finally:
        if voicelive_task and not voicelive_task.done():
            voicelive_task.cancel()
            try:
                await voicelive_task
            except asyncio.CancelledError:
                pass
        if session:
            await session_manager.cleanup_session(session.session_id)
