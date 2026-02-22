import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import websockets
from azure.identity.aio import DefaultAzureCredential

from app.backend.config import settings

logger = logging.getLogger(__name__)

_VOICELIVE_SCOPE = "https://cognitiveservices.azure.com/.default"
_MAX_RECONNECT_ATTEMPTS = 3
_RECONNECT_BASE_DELAY = 1.0


class VoiceLiveService:
    def __init__(self) -> None:
        self._credential: DefaultAzureCredential | None = None
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._connected = False
        self._receive_task: asyncio.Task[None] | None = None
        self._event_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def connect(self) -> None:
        self._credential = DefaultAzureCredential()
        token = await self._credential.get_token(_VOICELIVE_SCOPE)

        endpoint = settings.azure_voicelive_endpoint.rstrip("/")
        url = (
            f"{endpoint}"
            f"?api-version={settings.azure_voicelive_api_version}"
            f"&model={settings.azure_voicelive_model}"
        )

        if url.startswith("https://"):
            url = "wss://" + url[len("https://"):]
        elif url.startswith("http://"):
            url = "ws://" + url[len("http://"):]

        headers = {"Authorization": f"Bearer {token.token}"}
        self._ws = await websockets.connect(url, additional_headers=headers)
        self._connected = True

        await self._send_session_config()
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def _send_session_config(self) -> None:
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "input_audio_transcription": {"model": "azure-speech"},
                "turn_detection": {
                    "type": "azure_semantic_vad",
                    "create_response": False,
                    "silence_duration_ms": 500,
                    "remove_filler_words": True,
                },
                "input_audio_noise_reduction": {
                    "type": "azure_deep_noise_suppression"
                },
                "input_audio_echo_cancellation": {
                    "type": "server_echo_cancellation"
                },
            },
        }
        await self._send_json(config)

    async def _send_json(self, data: dict[str, Any]) -> None:
        if self._ws and self._connected:
            await self._ws.send(json.dumps(data))

    async def _receive_loop(self) -> None:
        try:
            async for raw in self._ws:
                try:
                    event = json.loads(raw)
                    await self._event_queue.put(event)
                except json.JSONDecodeError:
                    logger.warning("Non-JSON message from VoiceLive: %s", raw[:100])
        except websockets.ConnectionClosed:
            logger.info("VoiceLive WebSocket closed")
            self._connected = False
            await self._attempt_reconnect()
        except Exception:
            logger.exception("VoiceLive receive loop error")
            self._connected = False

    async def _attempt_reconnect(self) -> None:
        for attempt in range(1, _MAX_RECONNECT_ATTEMPTS + 1):
            delay = _RECONNECT_BASE_DELAY * (2 ** (attempt - 1))
            logger.info("VoiceLive reconnect attempt %d/%d in %.1fs", attempt, _MAX_RECONNECT_ATTEMPTS, delay)
            await asyncio.sleep(delay)
            try:
                await self.connect()
                logger.info("VoiceLive reconnected on attempt %d", attempt)
                return
            except Exception:
                logger.warning("VoiceLive reconnect attempt %d failed", attempt)
        logger.error("VoiceLive reconnection failed after %d attempts", _MAX_RECONNECT_ATTEMPTS)

    async def send_audio(self, base64_data: str) -> None:
        await self._send_json({
            "type": "input_audio_buffer.append",
            "audio": base64_data,
        })

    async def send_tts_request(self, text: str) -> None:
        await self._send_json({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "input_text", "text": text}],
            },
        })
        await self._send_json({"type": "response.create"})

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
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._credential:
            await self._credential.close()
            self._credential = None
