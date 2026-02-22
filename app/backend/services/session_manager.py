import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.backend.config import settings
from app.backend.models.session_state import SessionState
from app.backend.services.copilot_agent import CopilotAgent
from app.backend.services.voicelive_service import VoiceLiveService

logger = logging.getLogger(__name__)

_CLEANUP_INTERVAL_SECONDS = 60


class Session:
    def __init__(self, session_id: str, user_id: str) -> None:
        self.session_id = session_id
        self.user_id = user_id
        self.voicelive: VoiceLiveService = VoiceLiveService()
        self.copilot: CopilotAgent = CopilotAgent()
        self.state: SessionState = SessionState.IDLE
        self.created_at: datetime = datetime.now(timezone.utc)
        self.last_activity: datetime = datetime.now(timezone.utc)
        self.conversation_history: list[dict[str, Any]] = []
        self.turn_count: int = 0

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        elapsed = (datetime.now(timezone.utc) - self.last_activity).total_seconds()
        return elapsed > settings.session_ttl_seconds


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._user_sessions: dict[str, list[str]] = {}
        self._cleanup_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def create_session(self, user_id: str) -> Session:
        user_session_ids = self._user_sessions.get(user_id, [])
        if len(user_session_ids) >= settings.max_sessions_per_user:
            oldest_id = user_session_ids[0]
            await self.cleanup_session(oldest_id)

        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, user_id=user_id)

        try:
            await session.voicelive.connect()
        except Exception:
            logger.warning("VoiceLive connection failed, session will operate without voice", exc_info=True)

        try:
            await session.copilot.start()
        except Exception:
            logger.error("Copilot agent failed to start", exc_info=True)
            await session.voicelive.close()
            raise

        self._sessions[session_id] = session
        self._user_sessions.setdefault(user_id, []).append(session_id)

        logger.info("Created session %s for user %s", session_id, user_id)
        return session

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session not found: {session_id}")
        session.touch()
        return session

    async def cleanup_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if not session:
            return

        user_ids = self._user_sessions.get(session.user_id, [])
        if session_id in user_ids:
            user_ids.remove(session_id)
        if not user_ids:
            self._user_sessions.pop(session.user_id, None)

        try:
            await session.voicelive.close()
        except Exception:
            logger.warning("Error closing VoiceLive for session %s", session_id, exc_info=True)

        try:
            await session.copilot.close()
        except Exception:
            logger.warning("Error closing Copilot for session %s", session_id, exc_info=True)

        logger.info("Cleaned up session %s", session_id)

    async def cleanup_all(self) -> None:
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        session_ids = list(self._sessions.keys())
        for sid in session_ids:
            await self.cleanup_session(sid)

    async def _cleanup_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
                expired = [
                    sid for sid, session in self._sessions.items()
                    if session.is_expired()
                ]
                for sid in expired:
                    logger.info("Expiring session %s due to TTL", sid)
                    await self.cleanup_session(sid)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in session cleanup loop")

    @property
    def active_session_count(self) -> int:
        return len(self._sessions)


session_manager = SessionManager()
