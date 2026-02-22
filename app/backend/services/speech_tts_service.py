import asyncio
import base64
import logging
import re
from collections.abc import AsyncGenerator

from azure.identity.aio import DefaultAzureCredential

from app.backend.config import settings

logger = logging.getLogger(__name__)


# Regex to match most emoji/symbol Unicode blocks
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # misc symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols extended-A
    "\U00002702-\U000027B0"  # dingbats
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"              # zero-width joiner
    "\U000025A0-\U000025FF"  # geometric shapes
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002300-\U000023FF"  # misc technical
    "]+",
    flags=re.UNICODE,
)


def _sanitize_for_tts(text: str) -> str:
    """Strip markdown formatting and emoji so TTS reads natural prose."""
    # Remove emoji
    text = _EMOJI_RE.sub("", text)
    # Remove markdown bold/italic: **text**, __text__, *text*, _text_
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)
    # Remove markdown strikethrough: ~~text~~
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    # Remove markdown headings: ## Heading
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove markdown links: [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove inline code backticks: `code` → code
    text = re.sub(r"`{1,3}([^`]*)`{1,3}", r"\1", text)
    # Remove markdown bullet markers: - item, * item
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    # Remove numbered list markers: 1. item
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Remove markdown horizontal rules: --- or ***
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove markdown blockquote markers: > text
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Collapse multiple spaces (e.g. after emoji removal) and blank lines
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

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


        # Strip emoji and markdown so TTS reads natural prose
        text = _sanitize_for_tts(text)

        # Obtain an AAD token for the Cognitive Services resource
        token_response = await self._credential.get_token(
            "https://cognitiveservices.azure.com/.default"
        )

        resource_id = settings.azure_speech_service_id
        region = settings.azure_speech_region
        aad_token = token_response.token
        loop = asyncio.get_event_loop()
        def _do_synthesis() -> bytes:
            speech_config = speechsdk.SpeechConfig(
                auth_token=f"aad#{resource_id}#{aad_token}",
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