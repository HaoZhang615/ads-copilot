import asyncio
import json
import re
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter, ValidationError

from app.backend.models.session_state import SessionState
from app.backend.models.ws_messages import (
    AgentTextMessage,
    AudioMessage,
    AvatarAnswerMessage,
    AvatarIceMessage,
    AvatarIceRequest,
    AvatarOfferMessage,
    AvatarStateMessage,
    ControlMessage,
    ErrorMessage,
    IncomingMessage,
    SessionSummaryChunkMessage,
    StateMessage,
    TextMessage,
    TranscriptMessage,
    TtsAudioMessage,
    TtsStopMessage,
)

from app.backend.services.session_manager import Session, session_manager

logger = logging.getLogger(__name__)

router = APIRouter()

_incoming_adapter = TypeAdapter(IncomingMessage)

# Regex to strip fenced code blocks (```...```) from text before TTS.
# This prevents the avatar / audio TTS from reading out Mermaid diagrams,
# JSON snippets, or other code that the chat UI renders visually.
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
# Parenthetical source citations: "(Source: [label](url))" or "(Source: url)"
_SOURCE_CITATION_RE = re.compile(
    r"\(Source:\s*"           # literal "(Source:"
    r"(?:\[[^\]]*\]\([^)]*\)"  # markdown link [label](url)
    r"|[^)]+)"                # or bare text/url
    r"\)",                    # closing paren
    re.IGNORECASE,
)

# Standalone markdown links: [label](url) -> keep label only
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")

# Bare URLs: remove the entire sentence/clause containing a bare URL.
# This avoids orphaned filler like "See also: for more details." after the
# URL is stripped.  The URL part uses (?:[^\s.]|\.[^\s])+ so that a period
# is consumed only when followed by a non-space char (e.g. delta.io) — a
# sentence-ending period ('. ') is NOT swallowed.
_BARE_URL_SENTENCE_RE = re.compile(r"[^\n.]*https?://(?:[^\s.]|\.[^\s])+[^\n.]*\.?")
# Standalone "Sources:" lines (e.g. "Sources: Link1 . Link2")
# These appear at the end of MCP-grounded responses as a references block.
_SOURCES_LINE_RE = re.compile(r"^Sources?:\s*.*$", re.IGNORECASE | re.MULTILINE)

# Markdown emphasis: **bold**, *italic*, __bold__, _italic_
# Strip the markers but keep the enclosed text.
_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC_RE = re.compile(r"\*(.+?)\*")
_MD_BOLD2_RE = re.compile(r"__(.+?)__")
_MD_ITALIC2_RE = re.compile(r"_(.+?)_")


def _strip_for_tts(text: str) -> str:
    """Remove code blocks, source citations, URLs, and markdown for natural TTS."""
    cleaned = _CODE_BLOCK_RE.sub("", text)
    # Remove full "(Source: ...)" parenthetical citations
    cleaned = _SOURCE_CITATION_RE.sub("", cleaned)
    # Remove standalone "Sources: ..." reference lines
    cleaned = _SOURCES_LINE_RE.sub("", cleaned)
    # Convert remaining markdown links to just their label text
    cleaned = _MD_LINK_RE.sub(r"\1", cleaned)
    # Remove entire sentences/clauses that contain bare URLs
    cleaned = _BARE_URL_SENTENCE_RE.sub("", cleaned)
    # Strip markdown emphasis markers (keep enclosed text)
    cleaned = _MD_BOLD_RE.sub(r"\1", cleaned)
    cleaned = _MD_BOLD2_RE.sub(r"\1", cleaned)
    cleaned = _MD_ITALIC_RE.sub(r"\1", cleaned)
    cleaned = _MD_ITALIC2_RE.sub(r"\1", cleaned)
    # Collapse runs of 3+ newlines into 2 (paragraph break)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Collapse multiple spaces left by removals
    cleaned = re.sub(r"  +", " ", cleaned)
    return cleaned.strip()

async def _send_msg(ws: WebSocket, data: dict[str, Any]) -> None:
    try:
        await ws.send_json(data)
    except Exception:
        logger.debug("Failed to send WS message", exc_info=True)


async def _set_state(ws: WebSocket, session: Session, state: SessionState) -> None:
    session.state = state
    await _send_msg(ws, StateMessage(state=state).model_dump())


async def _handle_audio(ws: WebSocket, session: Session, msg: AudioMessage) -> None:
    if session.voicelive is None:
        return
    try:
        await session.voicelive.send_audio(msg.data)
    except Exception:
        await _send_msg(ws, ErrorMessage(message="Failed to send audio to VoiceLive").model_dump())


async def _cancel_tts(ws: WebSocket, session: Session) -> None:
    """Signal TTS cancellation and notify the frontend to stop playback.
    Always sends tts_stop to the frontend regardless of backend session
    state, because the backend finishes sending all TTS chunks almost
    instantly (they're pre-synthesized in memory) and transitions to IDLE
    long before the frontend finishes playing.  The frontend worklet queue
    may still have seconds of audio buffered.
    """
    session.tts_cancel_event.set()
    await _send_msg(ws, TtsStopMessage().model_dump())
    # Also stop avatar speech if connected
    if session.avatar_tts is not None and session.avatar_tts.is_connected:
        try:
            await session.avatar_tts.stop_speaking()
            await session.avatar_tts.disconnect_avatar()
            session.avatar_ready_event.clear()
            await _send_msg(ws, AvatarStateMessage(state="disconnected").model_dump())
        except Exception:
            logger.warning("Failed to stop avatar on barge-in", exc_info=True)
    logger.info("Barge-in: TTS stop sent to frontend")


async def _handle_avatar_offer(
    ws: WebSocket, session: Session, msg: AvatarOfferMessage
) -> asyncio.Task[None] | None:
    """Exchange SDP with the avatar service and return the answer.

    Spawns the (slow) avatar connection as a background task so the WS
    receive loop is never blocked.  Returns the task reference for cleanup.
    """
    if session.avatar_tts is None:
        await _send_msg(ws, ErrorMessage(message="Avatar not enabled").model_dump())
        return None

    async def _do_avatar_exchange() -> None:
        await _send_msg(ws, AvatarStateMessage(state="connecting").model_dump())
        try:
            server_sdp, ice_servers = await session.avatar_tts.connect_avatar(msg.sdp)
            await _send_msg(
                ws,
                AvatarAnswerMessage(sdp=server_sdp, ice_servers=ice_servers).model_dump(),
            )
            await _send_msg(ws, AvatarStateMessage(state="idle").model_dump())
            # Signal that avatar is ready for TTS
            session.avatar_ready_event.set()
        except Exception:
            logger.exception("Avatar SDP exchange failed")
            session.avatar_ready_event.clear()
            await _send_msg(ws, AvatarStateMessage(state="disconnected").model_dump())
            await _send_msg(ws, ErrorMessage(message="Avatar connection failed").model_dump())

    return asyncio.create_task(_do_avatar_exchange(), name="avatar-offer")


async def _handle_avatar_ice_request(
    ws: WebSocket, session: Session
) -> None:
    """Return cached ICE relay servers so the browser can create a peer connection."""
    if session.avatar_tts is None:
        await _send_msg(ws, ErrorMessage(message="Avatar not enabled").model_dump())
        return

    try:
        ice_token = session.avatar_tts._ice_token or {}
        if not ice_token:
            await session.avatar_tts._refresh_ice_token()
            ice_token = session.avatar_tts._ice_token or {}
        ice_servers = [{
            "urls": ice_token.get("Urls", []),
            "username": ice_token.get("Username", ""),
            "credential": ice_token.get("Password", ""),
        }]
        await _send_msg(ws, AvatarIceMessage(ice_servers=ice_servers).model_dump())
        logger.info("Sent ICE servers to frontend: %s", ice_token.get("Urls", []))
    except Exception:
        logger.exception("Failed to get ICE servers")
        await _send_msg(ws, ErrorMessage(message="Failed to get ICE servers").model_dump())


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
            # Always send is_final so the frontend clears its tracking ref.
            # Without this, if the agent produces no text (e.g. only tool
            # calls), currentAssistantIdRef on the frontend stays stale and
            # the next response's chunks get appended to the wrong bubble.
            await _send_msg(ws, AgentTextMessage(text=final_text, is_final=True).model_dump())
            session.conversation_history.append({"role": "assistant", "content": final_text})

            # In lite mode, skip all TTS / avatar speech.
            tts_text = ""
            if not session.lite_mode:
                tts_text = _strip_for_tts(final_text) if final_text else ""
            if tts_text:
                await _set_state(ws, session, SessionState.SPEAKING)
                # Clear cancellation flag before starting TTS
                session.tts_cancel_event.clear()
                # Wait for avatar WebRTC handshake to complete (if in progress)
                # The frontend fires avatar_ice_request on state="thinking",
                # so the avatar exchange runs in parallel with agent streaming.
                # Give it up to 15s to finish before falling back to audio TTS.
                avatar_connected = False
                if session.avatar_tts is not None:
                    avatar_connected = session.avatar_tts.is_connected
                    if not avatar_connected:
                        logger.info("TTS: avatar not yet connected, waiting up to 15s for avatar_ready_event")
                        try:
                            await asyncio.wait_for(session.avatar_ready_event.wait(), timeout=15.0)
                            avatar_connected = session.avatar_tts.is_connected
                            logger.info("TTS: avatar_ready_event fired, is_connected=%s", avatar_connected)
                        except asyncio.TimeoutError:
                            logger.info("TTS: avatar_ready_event timed out, falling back to audio TTS")
                            avatar_connected = False
                if avatar_connected and session.avatar_tts is not None:
                    # Avatar path: speak through WebRTC stream (no audio chunks)
                    logger.info(
                        "TTS: speaking %d chars via Avatar WebRTC", len(tts_text)
                    )
                    try:
                        await _send_msg(
                            ws,
                            AvatarStateMessage(state="speaking").model_dump(),
                        )
                        await session.avatar_tts.speak(tts_text)
                        # Keep avatar connected for the next turn to avoid
                        # 4429 throttling from rapid connect/disconnect cycles.
                        # The connection is torn down on barge-in (_cancel_tts)
                        # or session cleanup.
                        await _send_msg(
                            ws,
                            AvatarStateMessage(state="idle").model_dump(),
                        )
                    except Exception:
                        logger.warning("Avatar speak failed", exc_info=True)
                        # Connection may be broken — disconnect and let next
                        # turn reconnect.
                        try:
                            await session.avatar_tts.disconnect_avatar()
                        except Exception:
                            pass
                        session.avatar_ready_event.clear()
                        await _send_msg(
                            ws,
                            AvatarStateMessage(state="disconnected").model_dump(),
                        )
                elif session.speech_tts is not None:
                    # Regular audio path: stream TTS chunks to frontend
                    logger.info(
                        "TTS: synthesizing %d chars via Azure Speech SDK",
                        len(tts_text),
                    )
                    try:
                        async for audio_chunk in session.speech_tts.synthesize(tts_text):
                            # Check if barge-in was requested
                            if session.tts_cancel_event.is_set():
                                logger.info("TTS: stopping chunk delivery due to barge-in")
                                break
                            await _send_msg(ws, TtsAudioMessage(data=audio_chunk).model_dump())
                    except Exception:
                        logger.warning("TTS synthesis failed", exc_info=True)

        except Exception:
            logger.exception("Error processing agent response")
            await _send_msg(ws, ErrorMessage(message="Error processing your message").model_dump())
        finally:
            # Only transition to IDLE if the session is still in an agent-owned
            # state (THINKING or SPEAKING).  If the user toggled the mic on
            # while the agent was running, the state will already be LISTENING
            # — we must not overwrite that or the mic appears "broken".
            if session.state in (SessionState.THINKING, SessionState.SPEAKING):
                await _set_state(ws, session, SessionState.IDLE)


async def _handle_text(
    ws: WebSocket,
    session: Session,
    msg: TextMessage,
    agent_lock: asyncio.Lock,
) -> asyncio.Task[None]:
    """Kick off agent processing in a background task (non-blocking)."""
    # Cancel any ongoing TTS when user sends a text message
    await _cancel_tts(ws, session)
    return asyncio.create_task(
        _process_agent_response(ws, session, msg.content, agent_lock),
        name="agent-text",
    )


async def _generate_session_summary(
    ws: WebSocket,
    session: Session,
    agent_lock: asyncio.Lock,
) -> None:
    """Generate and stream a session summary document to the frontend.

    Called before session cleanup when the user ends the session.
    Streams the summary as `session_summary_chunk` messages, then
    sends a final chunk with `is_final=True`.
    """
    async with agent_lock:
        await _set_state(ws, session, SessionState.THINKING)
        full_summary: list[str] = []
        try:
            async for chunk in session.copilot.generate_summary(
                session.conversation_history
            ):
                full_summary.append(chunk)
                await _send_msg(
                    ws,
                    SessionSummaryChunkMessage(text=chunk, is_final=False).model_dump(),
                )

            # Send the final consolidated summary
            final_text = "".join(full_summary)
            await _send_msg(
                ws,
                SessionSummaryChunkMessage(text=final_text, is_final=True).model_dump(),
            )
        except Exception:
            logger.exception("Error generating session summary")
            await _send_msg(
                ws,
                ErrorMessage(message="Failed to generate session summary").model_dump(),
            )
        finally:
            # Now clean up the session
            await session_manager.cleanup_session(session.session_id)
            await _set_state(ws, session, SessionState.IDLE)


async def _handle_control(
    ws: WebSocket,
    session: Session,
    msg: ControlMessage,
    agent_lock: asyncio.Lock,
) -> asyncio.Task[None] | None:
    if msg.action == "start_session":
        await _send_msg(ws, StateMessage(state=session.state).model_dump())

    elif msg.action == "end_session":
        # Cancel any ongoing TTS before generating summary
        await _cancel_tts(ws, session)
        # Generate summary in background, then clean up
        return asyncio.create_task(
            _generate_session_summary(ws, session, agent_lock),
            name="session-summary",
        )

    elif msg.action == "start_listening":
        # User started mic capture — cancel any ongoing TTS (barge-in)
        await _cancel_tts(ws, session)
        # Ensure VoiceLive connection is healthy before audio flows
        if session.voicelive is not None:
            try:
                await session.voicelive.ensure_connected()
            except Exception:
                logger.warning("VoiceLive reconnect on start_listening failed", exc_info=True)
                await _send_msg(ws, ErrorMessage(message="Voice connection lost. Please try again.").model_dump())
        await _set_state(ws, session, SessionState.LISTENING)

    elif msg.action == "stop_listening":
        # Only go to IDLE if the session is currently LISTENING.
        # If the agent is THINKING/SPEAKING, let it keep that state.
        if session.state == SessionState.LISTENING:
            await _set_state(ws, session, SessionState.IDLE)

    elif msg.action == "tts_stop":
        # User explicitly pressed stop audio button
        await _cancel_tts(ws, session)

    return None

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
                    # Barge-in: if TTS is playing and user starts speaking, stop it
                    await _cancel_tts(ws, session)
                    await _send_msg(ws, TranscriptMessage(text=text, is_final=False).model_dump())

            elif event_type == "input_audio_buffer.speech_started":
                # VoiceLive detected speech start — immediate barge-in
                await _cancel_tts(ws, session)

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
        lite_mode = websocket.query_params.get("lite", "").lower() in ("1", "true")
        session = await session_manager.create_session(user_id, lite_mode=lite_mode)
        await _send_msg(websocket, {
            "type": "session_created",
            "session_id": session.session_id,
            "lite_mode": session.lite_mode,
        })
        await _send_msg(websocket, StateMessage(state=session.state).model_dump())
        # VoiceLive listener is only needed in full (non-lite) mode.
        if session.voicelive is not None:
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
                control_task = await _handle_control(websocket, session, msg, agent_lock)
                if control_task is not None:
                    agent_tasks.append(control_task)
            elif isinstance(msg, AvatarOfferMessage):
                avatar_task = await _handle_avatar_offer(websocket, session, msg)
                if avatar_task is not None:
                    agent_tasks.append(avatar_task)
            elif isinstance(msg, AvatarIceRequest):
                await _handle_avatar_ice_request(websocket, session)

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
