from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field

from app.backend.models.session_state import SessionState


class AudioMessage(BaseModel):
    type: Literal["audio"] = "audio"
    data: str


class ControlMessage(BaseModel):
    type: Literal["control"] = "control"
    action: Literal["start_listening", "stop_listening", "start_session", "end_session", "tts_stop"]


class TextMessage(BaseModel):
    type: Literal["text"] = "text"
    content: str


class AvatarOfferMessage(BaseModel):
    type: Literal["avatar_offer"] = "avatar_offer"
    sdp: str


class AvatarIceRequest(BaseModel):
    type: Literal["avatar_ice_request"] = "avatar_ice_request"


class RestoreHistoryMessage(BaseModel):
    """Sent by the frontend after a mode toggle reconnect to restore conversation context."""
    type: Literal["restore_history"] = "restore_history"
    messages: list[dict[str, str]]

IncomingMessage = Annotated[
    Union[AudioMessage, ControlMessage, TextMessage, AvatarOfferMessage, AvatarIceRequest, RestoreHistoryMessage],
    Field(discriminator="type"),
]


class TranscriptMessage(BaseModel):
    type: Literal["transcript"] = "transcript"
    text: str
    is_final: bool


class AgentTextMessage(BaseModel):
    type: Literal["agent_text"] = "agent_text"
    text: str
    is_final: bool


class TtsAudioMessage(BaseModel):
    type: Literal["tts_audio"] = "tts_audio"
    data: str


class TtsStopMessage(BaseModel):
    type: Literal["tts_stop"] = "tts_stop"


class AvatarAnswerMessage(BaseModel):
    type: Literal["avatar_answer"] = "avatar_answer"
    sdp: str
    ice_servers: list[dict[str, Any]]


class AvatarStateMessage(BaseModel):
    type: Literal["avatar_state"] = "avatar_state"
    state: Literal["idle", "connecting", "speaking", "disconnected"]


class AvatarIceMessage(BaseModel):
    type: Literal["avatar_ice"] = "avatar_ice"
    ice_servers: list[dict[str, Any]]

class StateMessage(BaseModel):
    type: Literal["state"] = "state"
    state: SessionState


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    message: str


class SessionSummaryChunkMessage(BaseModel):
    """Streaming chunk of the session summary document."""
    type: Literal["session_summary_chunk"] = "session_summary_chunk"
    text: str
    is_final: bool


OutgoingMessage = Union[
    TranscriptMessage,
    AgentTextMessage,
    TtsAudioMessage,
    TtsStopMessage,
    AvatarAnswerMessage,
    AvatarIceMessage,
    AvatarStateMessage,
    StateMessage,
    ErrorMessage,
    SessionSummaryChunkMessage,
]
