import asyncio
import logging
from collections.abc import AsyncGenerator

from copilot import CopilotClient, CopilotSession, SessionEvent

from app.backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an Azure Databricks solutions architect conducting an Architecture "
    "Design Session (ADS). Follow the structured workflow defined in your loaded "
    "skill to gather requirements and produce architecture recommendations."
)

_SKILL_DIRECTORIES = ["./databricks-ads-session"]

# Sentinel to signal end of streaming
_STREAM_DONE = object()


class CopilotAgent:
    def __init__(self) -> None:
        self._client: CopilotClient | None = None
        self._session: CopilotSession | None = None
        self._conversation_history: list[dict[str, str]] = []
        self._unsubscribe: callable | None = None

    async def start(self) -> None:
        options: dict = {}
        if settings.copilot_github_token:
            options["github_token"] = settings.copilot_github_token
            options["use_logged_in_user"] = False

        self._client = CopilotClient(options or None)
        await self._client.start()

        self._session = await self._client.create_session({
            "model": "claude-sonnet-4.6",
            "skill_directories": _SKILL_DIRECTORIES,
            "system_message": {"content": _SYSTEM_PROMPT},
        })

        # Warm-up: send a hidden message to force skill loading so the
        # first real user message doesn't stall.
        logger.info("Copilot warm-up: priming session…")
        try:
            async for _ in self.send_message("hello"):
                pass  # drain the response
            logger.info("Copilot warm-up complete")
            # Clear warm-up from history so it doesn't leak into the real conversation
            self._conversation_history.clear()
        except Exception:
            logger.warning("Copilot warm-up failed (non-fatal)", exc_info=True)
            self._conversation_history.clear()

    async def send_message(self, text: str) -> AsyncGenerator[str, None]:
        """Send a message and yield streaming delta chunks."""
        if not self._client or not self._session:
            raise RuntimeError("CopilotAgent not started")

        self._conversation_history.append({"role": "user", "content": text})

        queue: asyncio.Queue = asyncio.Queue()
        full_response: list[str] = []

        def _event_handler(event: SessionEvent) -> None:
            event_type = event.type.value if hasattr(event.type, 'value') else str(event.type)

            if event_type == "assistant.message_delta":
                delta = event.data.delta_content or ""
                if delta:
                    queue.put_nowait(delta)
            elif event_type == "assistant.message":
                # Full message (non-delta) — might arrive if not streaming
                content = event.data.content or ""
                if content:
                    queue.put_nowait(content)
            elif event_type == "assistant.turn_end":
                queue.put_nowait(_STREAM_DONE)
            elif event_type == "session.error":
                error_msg = event.data.message or "Unknown Copilot error"
                logger.error("Copilot session error: %s", error_msg)
                queue.put_nowait(_STREAM_DONE)
            elif event_type in (
                "assistant.tool_call",
                "assistant.tool_call_delta",
                "assistant.tool_result",
            ):
                # Tool calls (e.g. generate_architecture.py) produce
                # events without text deltas — just reset the per-chunk
                # timeout so we don't mistakenly abort.
                logger.debug("Copilot tool event: %s", event_type)
                queue.put_nowait(None)  # keep-alive sentinel
        unsubscribe = self._session.on(_event_handler)

        try:
            # send() returns a message ID, streaming happens via events
            await self._session.send({"prompt": text})

            while True:
                try:
                    chunk = await asyncio.wait_for(queue.get(), timeout=300.0)
                except asyncio.TimeoutError:
                    logger.warning("Copilot response timed out after 300s")
                    break

                if chunk is _STREAM_DONE:
                    break
                # Skip keep-alive sentinels from tool-call events
                if chunk is None:
                    continue
                full_response.append(chunk)
                yield chunk
        finally:
            unsubscribe()

        self._conversation_history.append({
            "role": "assistant",
            "content": "".join(full_response),
        })

    @property
    def conversation_history(self) -> list[dict[str, str]]:
        return self._conversation_history

    async def stop(self) -> None:
        if self._session:
            try:
                await self._session.destroy()
            except Exception:
                logger.warning("Error destroying Copilot session", exc_info=True)
            self._session = None

        if self._client:
            try:
                self._client.stop()
            except Exception:
                logger.warning("Error stopping CopilotClient", exc_info=True)
            self._client = None
