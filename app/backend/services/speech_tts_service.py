import asyncio
import base64
import logging
from collections.abc import AsyncGenerator

from azure.identity.aio import DefaultAzureCredential

from app.backend.config import settings

logger = logging.getLogger(__name__)


class SpeechTtsService:
    """Azure Speech SDK text-to-speech service.

    The Speech SDK is synchronous, so synthesis runs in a thread-pool
    executor to avoid blocking the async event loop.
    """

    def __init__(self) -> None:
        self._credential: DefaultAzureCredential | None = None

    async def start(self) -> None:
        self._credential = DefaultAzureCredential()

    async def synthesize(self, text: str) -> AsyncGenerator[str, None]:
        """Synthesize *text* to PCM16 24 kHz audio, yielding base64 chunks."""
        import azure.cognitiveservices.speech as speechsdk

        if not self._credential:
            raise RuntimeError("SpeechTtsService not started")

        # Obtain an AAD token for the Cognitive Services resource
        token_response = await self._credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )

        endpoint = settings.azure_voicelive_endpoint.rstrip("/")
        region = settings.azure_speech_region
        aad_token = token_response.token

        loop = asyncio.get_event_loop()

        def _do_synthesis() -> bytes:
            speech_config = speechsdk.SpeechConfig(
                auth_token=f"aad#{endpoint}#{aad_token}",
                region=region,
            )
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm
            )
            speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"

            # Synthesize into memory (no file / speaker output)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None,
            )

            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data  # raw PCM bytes

            cancellation = result.cancellation_details
            raise RuntimeError(
                f"Speech synthesis failed: {result.reason} — "
                f"{cancellation.reason}: {cancellation.error_details}"
            )

        audio_bytes = await loop.run_in_executor(None, _do_synthesis)

        # Chunk into ~4800-byte pieces (100 ms at 24 kHz / 16-bit mono = 4800 bytes)
        chunk_size = 4800
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i : i + chunk_size]
            yield base64.b64encode(chunk).decode("ascii")

    async def close(self) -> None:
        if self._credential:
            await self._credential.close()
            self._credential = None