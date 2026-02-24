import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any

from azure.ai.voicelive.aio import connect, VoiceLiveConnection
from azure.identity.aio import DefaultAzureCredential

from app.backend.config import settings

logger = logging.getLogger(__name__)

_MAX_RECONNECT_ATTEMPTS = 3
_RECONNECT_BASE_DELAY = 1.0


class VoiceLiveService:
    def __init__(self) -> None:
        self._credential: DefaultAzureCredential | None = None
        self._connection: VoiceLiveConnection | None = None
        self._connected = False
        self._reconnecting = False
        self._receive_task: asyncio.Task[None] | None = None
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._ctx_manager: Any = None

    async def connect(self) -> None:
        self._credential = DefaultAzureCredential()

        endpoint = settings.azure_voicelive_endpoint.rstrip("/")
        model = settings.azure_voicelive_model or None

        self._ctx_manager = connect(
            credential=self._credential,
            endpoint=endpoint,
            api_version=settings.azure_voicelive_api_version,
            model=model,
        )
        self._connection = await self._ctx_manager.__aenter__()
        self._connected = True

        await self._send_session_config()
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def _send_session_config(self) -> None:
        if not self._connection:
            return

        await self._connection.session.update(
            session={
                "modalities": ["audio", "text"],
                "input_audio_transcription": {"model": "azure-speech"},
                "turn_detection": {
                    "type": "azure_semantic_vad",
                    "create_response": False,
                    "silence_duration_ms": 1500,
                    "remove_filler_words": True,
                },
                "input_audio_noise_reduction": {
                    "type": "azure_deep_noise_suppression",
                },
                "input_audio_echo_cancellation": {
                    "type": "server_echo_cancellation",
                },
            },
        )

    async def _receive_loop(self) -> None:
        if not self._connection:
            return

        try:
            async for event in self._connection:
                try:
                    event_dict = event.as_dict() if hasattr(event, "as_dict") else dict(event)
                    await self._event_queue.put(event_dict)
                except Exception:
                    logger.warning("Failed to process VoiceLive event", exc_info=True)
        except Exception:
            logger.exception("VoiceLive receive loop error")
            self._connected = False
            await self._attempt_reconnect()

    async def _attempt_reconnect(self) -> None:
        for attempt in range(1, _MAX_RECONNECT_ATTEMPTS + 1):
            delay = _RECONNECT_BASE_DELAY * (2 ** (attempt - 1))
            logger.info(
                "VoiceLive reconnect attempt %d/%d in %.1fs",
                attempt, _MAX_RECONNECT_ATTEMPTS, delay,
            )
            await asyncio.sleep(delay)
            try:
                await self.connect()
                logger.info("VoiceLive reconnected on attempt %d", attempt)
                return
            except Exception:
                logger.warning("VoiceLive reconnect attempt %d failed", attempt)
        logger.error("VoiceLive reconnection failed after %d attempts", _MAX_RECONNECT_ATTEMPTS)

    async def send_audio(self, base64_data: str) -> None:
        if self._connection and self._connected:
            try:
                await self._connection.input_audio_buffer.append(audio=base64_data)
            except Exception as exc:
                # Detect closed/closing transport and trigger reconnection
                exc_str = str(exc).lower()
                if "closing" in exc_str or "closed" in exc_str:
                    logger.warning("VoiceLive transport closed during send_audio, reconnecting")
                    self._connected = False
                    await self.ensure_connected()
                else:
                    raise

    async def ensure_connected(self) -> None:
        """Verify the VoiceLive connection is alive; reconnect if not.

        Safe to call multiple times concurrently — only one reconnection
        attempt will run at a time.
        """
        if self._connected:
            return
        if self._reconnecting:
            # Another coroutine is already reconnecting; wait for it
            for _ in range(50):  # up to 5s
                await asyncio.sleep(0.1)
                if self._connected:
                    return
            return
        self._reconnecting = True
        try:
            # Clean up stale connection before reconnecting
            await self._close_connection()
            await self._attempt_reconnect()
        finally:
            self._reconnecting = False

    async def _close_connection(self) -> None:
        """Tear down the existing connection resources without resetting credential."""
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None
        if self._ctx_manager:
            try:
                await self._ctx_manager.__aexit__(None, None, None)
            except Exception:
                logger.debug("Error closing stale VoiceLive connection", exc_info=True)
            self._ctx_manager = None
            self._connection = None

    async def receive_events(self) -> AsyncGenerator[dict[str, Any], None]:
        while self._connected or not self._event_queue.empty():
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                yield event
            except asyncio.TimeoutError:
                if not self._connected:
                    break

    async def close(self) -> None:
        self._connected = False
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        if self._ctx_manager:
            try:
                await self._ctx_manager.__aexit__(None, None, None)
            except Exception:
                logger.warning("Error closing VoiceLive connection", exc_info=True)
            self._ctx_manager = None
            self._connection = None
        if self._credential:
            await self._credential.close()
            self._credential = None
