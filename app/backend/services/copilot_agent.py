import logging
from collections.abc import AsyncGenerator
from typing import Any

from github_copilot_sdk import CopilotClient

from app.backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an Azure Databricks solutions architect conducting an Architecture "
    "Design Session (ADS). Follow the structured workflow defined in your loaded "
    "skill to gather requirements and produce architecture recommendations."
)

_SKILL_DIRECTORIES = ["./databricks-ads-session"]


class CopilotAgent:
    def __init__(self) -> None:
        self._client: CopilotClient | None = None
        self._session_id: str | None = None
        self._conversation_history: list[dict[str, str]] = []

    async def start(self) -> None:
        self._client = CopilotClient(token=settings.github_token)
        await self._client.start()

        session = await self._client.create_session({
            "model": "claude-sonnet-4.6",
            "skill_directories": _SKILL_DIRECTORIES,
            "system_prompt": _SYSTEM_PROMPT,
        })
        self._session_id = session.get("session_id") or session.get("id")

    async def send_message(self, text: str) -> AsyncGenerator[str, None]:
        if not self._client or not self._session_id:
            raise RuntimeError("CopilotAgent not started")

        self._conversation_history.append({"role": "user", "content": text})

        full_response: list[str] = []
        async for chunk in self._client.send_message(
            session_id=self._session_id,
            message=text,
            stream=True,
        ):
            content = _extract_content(chunk)
            if content:
                full_response.append(content)
                yield content

        self._conversation_history.append({
            "role": "assistant",
            "content": "".join(full_response),
        })

    @property
    def conversation_history(self) -> list[dict[str, str]]:
        return self._conversation_history

    async def close(self) -> None:
        if self._client:
            try:
                await self._client.close()
            except Exception:
                logger.warning("Error closing CopilotClient", exc_info=True)
            self._client = None
            self._session_id = None


def _extract_content(chunk: Any) -> str:
    if isinstance(chunk, str):
        return chunk
    if isinstance(chunk, dict):
        return chunk.get("content", "") or chunk.get("text", "") or chunk.get("delta", "")
    if hasattr(chunk, "content"):
        return chunk.content or ""
    if hasattr(chunk, "delta"):
        return chunk.delta or ""
    return str(chunk) if chunk else ""
