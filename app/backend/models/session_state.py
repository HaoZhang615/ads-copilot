from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SessionState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


class SessionInfo(BaseModel):
    session_id: str
    state: SessionState
    created_at: datetime
    last_activity: datetime
    turn_count: int
