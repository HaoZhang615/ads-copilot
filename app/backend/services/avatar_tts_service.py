import asyncio
import json
import logging
from typing import Any

import aiohttp
from azure.identity.aio import DefaultAzureCredential

from app.backend.config import settings

logger = logging.getLogger(__name__)

_ICE_TOKEN_REFRESH_SECONDS = 60 * 60 * 23  # ~23 hours
_AVATAR_CONNECT_TIMEOUT = 30  # seconds to wait for avatar WebRTC handshake
_AVATAR_RETRY_MAX = 3  # max retries for transient errors (e.g. 4429 throttling)
_AVATAR_RETRY_BASE_DELAY = 2.0  # base delay in seconds (exponential backoff)


class AvatarTtsService:
    """Azure Speech SDK text-to-speech avatar service.

    Uses the SpeechSynthesizer with the enableTalkingAvatar WebSocket
    endpoint.  The avatar is connected on-demand (connect-on-demand) to
    avoid GPU billing when idle.

    Lifecycle per turn:
      1. connect_avatar(client_sdp) -> (server_sdp, ice_servers)
      2. speak(text) -> speaks through WebRTC stream
      3. disconnect_avatar() -> tears down connection, stops billing
    """

    def __init__(self) -> None:
        self._credential: DefaultAzureCredential | None = None
        self._ice_token: dict[str, Any] | None = None
        self._synthesizer: Any | None = None  # speechsdk.SpeechSynthesizer
        self._connection: Any | None = None  # speechsdk.Connection
        self._connected = False

    async def start(self) -> None:
        """Initialize credentials and fetch initial ICE token."""
        self._credential = DefaultAzureCredential()
        await self._refresh_ice_token()

    async def _refresh_ice_token(self) -> None:
        """Fetch ICE relay token from Azure Speech service."""
        region = settings.azure_speech_region
        resource_id = settings.azure_speech_service_id

        if self._credential is None:
            raise RuntimeError("AvatarTtsService.start() must be called first")
        token_response = await self._credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )
        aad_token = token_response.token

        url = (
            f"https://{region}.tts.speech.microsoft.com"
            f"/cognitiveservices/avatar/relay/token/v1"
        )
        headers = {"Authorization": f"Bearer aad#{resource_id}#{aad_token}"}

        logger.info("Fetching ICE token from %s with resource_id=%s", url, resource_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(
                        f"Failed to fetch ICE token: {resp.status} {body}"
                    )
                self._ice_token = json.loads(await resp.text())
                logger.info("ICE token refreshed")

    async def connect_avatar(self, client_sdp: str) -> tuple[str, list[dict[str, Any]]]:
        """Establish WebRTC avatar connection.

        Args:
            client_sdp: The SDP offer from the browser.

        Returns:
            Tuple of (server_sdp_answer, ice_servers).
        """
        import azure.cognitiveservices.speech as speechsdk

        # Always clean up any previous synthesizer (even from failed attempts)
        if self._connected or self._synthesizer:
            await self.disconnect_avatar()

        if not self._ice_token:
            await self._refresh_ice_token()

        region = settings.azure_speech_region
        resource_id = settings.azure_speech_service_id

        if self._credential is None:
            raise RuntimeError("AvatarTtsService.start() must be called first")
        token_response = await self._credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )
        aad_token = token_response.token

        loop = asyncio.get_event_loop()

        def _do_connect():
            logger.info(
                "Avatar _do_connect: creating SpeechConfig endpoint=wss://%s...enableTalkingAvatar, voice=%s",
                region, settings.avatar_voice,
            )
            speech_config = speechsdk.SpeechConfig(
                endpoint=(
                    f"wss://{region}.tts.speech.microsoft.com"
                    f"/cognitiveservices/websocket/v1"
                    f"?enableTalkingAvatar=true"
                ),
            )
            speech_config.authorization_token = f"aad#{resource_id}#{aad_token}"
            speech_config.speech_synthesis_voice_name = settings.avatar_voice
            logger.info("Avatar _do_connect: creating SpeechSynthesizer")
            self._synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
            ice = self._ice_token or {}
            logger.info(
                "Avatar _do_connect: ICE urls=%s, username=%s",
                ice.get("Urls", []), ice.get("Username", "<none>"),
            )
            avatar_config = {
                "synthesis": {
                    "video": {
                        "protocol": {
                            "name": "WebRTC",
                            "webrtcConfig": {
                                "clientDescription": client_sdp,
                                "iceServers": [{
                                    "urls": [ice.get("Urls", [""])[0]],
                                    "username": ice.get("Username", ""),
                                    "credential": ice.get("Password", ""),
                                }],
                            },
                        },
                        "format": {
                            "crop": {
                                "topLeft": {"x": 600, "y": 0},
                                "bottomRight": {"x": 1320, "y": 1080},
                            },
                            "bitrate": 1000000,
                        },
                        "talkingAvatar": {
                            "customized": False,
                            "character": settings.avatar_character,
                            "style": settings.avatar_style,
                            "background": {
                                "color": "#FFFFFFFF",
                            },
                        },
                    }
                }
            }
            connection = speechsdk.Connection.from_speech_synthesizer(
                self._synthesizer
            )
            connection.set_message_property(
                "speech.config", "context", json.dumps(avatar_config)
            )
            self._connection = connection
            logger.info("Avatar _do_connect: set avatar config, calling speak_text_async('')")
            # Send empty text to trigger connection & get remote SDP
            result = self._synthesizer.speak_text_async("").get()
            logger.info("Avatar _do_connect: speak_text_async returned, reason=%s", result.reason)
            if result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                raise RuntimeError(
                    f"Avatar connection failed: {details.reason} — "
                    f"{details.error_details}"
                )

            turn_start_raw = self._synthesizer.properties.get_property_by_name(
                "SpeechSDKInternal-ExtraTurnStartMessage"
            )
            logger.info("Avatar _do_connect: ExtraTurnStartMessage length=%d", len(turn_start_raw or ""))
            if not turn_start_raw:
                raise RuntimeError("Avatar connection: ExtraTurnStartMessage is empty — no remote SDP")
            turn_start = json.loads(turn_start_raw)
            remote_sdp = turn_start["webrtc"]["connectionString"]
            logger.info("Avatar _do_connect: got remote SDP (%d chars)", len(remote_sdp))
            return remote_sdp

        logger.info("Avatar connect_avatar: running _do_connect in executor with %ds timeout", _AVATAR_CONNECT_TIMEOUT)
        last_error: Exception | None = None
        for attempt in range(1, _AVATAR_RETRY_MAX + 1):
            try:
                remote_sdp = await asyncio.wait_for(
                    loop.run_in_executor(None, _do_connect),
                    timeout=_AVATAR_CONNECT_TIMEOUT,
                )
                break  # success
            except asyncio.TimeoutError:
                logger.error(
                    "Avatar connect_avatar: timed out after %ds (attempt %d/%d)",
                    _AVATAR_CONNECT_TIMEOUT, attempt, _AVATAR_RETRY_MAX,
                )
                await self.disconnect_avatar()
                last_error = RuntimeError(
                    f"Avatar connection timed out after {_AVATAR_CONNECT_TIMEOUT}s"
                )
            except Exception as exc:
                logger.error(
                    "Avatar connect_avatar: _do_connect failed (attempt %d/%d)",
                    attempt, _AVATAR_RETRY_MAX, exc_info=True,
                )
                await self.disconnect_avatar()
                last_error = exc
                # Only retry on throttling (4429) errors
                if "4429" not in str(exc):
                    raise

            if attempt < _AVATAR_RETRY_MAX:
                delay = _AVATAR_RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.info("Avatar connect_avatar: retrying in %.1fs", delay)
                await asyncio.sleep(delay)
                # Re-clean before retry
                if self._connected or self._synthesizer:
                    await self.disconnect_avatar()
            else:
                raise last_error  # type: ignore[misc]
        self._connected = True
        logger.info("Avatar connected successfully")
        ice = self._ice_token or {}
        ice_servers = [{
            "urls": ice.get("Urls", []),
            "username": ice.get("Username", ""),
            "credential": ice.get("Password", ""),
        }]
        return remote_sdp, ice_servers

    async def speak(self, text: str) -> None:
        """Speak text through the connected avatar.

        The avatar lip-syncs and produces audio+video through the
        existing WebRTC stream.  This call blocks until speech is done.
        """
        import azure.cognitiveservices.speech as speechsdk

        if not self._synthesizer or not self._connected:
            raise RuntimeError("Avatar not connected")

        loop = asyncio.get_event_loop()
        synthesizer = self._synthesizer

        def _do_speak() -> None:
            result = synthesizer.speak_text_async(text).get()
            if result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                logger.warning(
                    "Avatar speak canceled: %s — %s",
                    details.reason, details.error_details,
                )

        await loop.run_in_executor(None, _do_speak)

    async def stop_speaking(self) -> None:
        """Interrupt the current avatar speech (barge-in)."""
        if not self._connection:
            return

        loop = asyncio.get_event_loop()
        connection = self._connection

        def _do_stop() -> None:
            try:
                stop_msg = json.dumps({"synthesis": {"control": {"action": "stop"}}})
                connection.send_message_async(
                    "synthesis.control", stop_msg
                ).get()
            except Exception:
                logger.warning("Failed to stop avatar speaking", exc_info=True)

        await loop.run_in_executor(None, _do_stop)

    async def disconnect_avatar(self) -> None:
        """Tear down the avatar WebRTC session to stop billing.

        Safe to call multiple times and even when the connection was never
        fully established (e.g. after a failed connect_avatar attempt).
        """
        self._connected = False
        loop = asyncio.get_event_loop()

        synthesizer = self._synthesizer
        self._synthesizer = None
        self._connection = None

        if synthesizer:
            def _do_close() -> None:
                try:
                    synthesizer.stop_speaking_async().get()
                except Exception:
                    pass

            try:
                await loop.run_in_executor(None, _do_close)
            except Exception:
                logger.warning("Avatar disconnect: error during synthesizer cleanup", exc_info=True)

        logger.info("Avatar disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def close(self) -> None:
        """Full cleanup — disconnect avatar and release credentials."""
        await self.disconnect_avatar()
        if self._credential:
            await self._credential.close()
            self._credential = None
