from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from app.backend.models.session_state import SessionState


class AudioMessage(BaseModel):
    type: Literal["audio"] = "audio"
    data: str


class ControlMessage(BaseModel):
    type: Literal["control"] = "control"
    action: Literal["start_listening", "stop_listening", "start_session", "end_session"]


class TextMessage(BaseModel):
    type: Literal["text"] = "text"
    content: str


IncomingMessage = Annotated[
    Union[AudioMessage, ControlMessage, TextMessage],
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

class StateMessage(BaseModel):
    type: Literal["state"] = "state"
    state: SessionState


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    message: str


OutgoingMessage = Union[
    TranscriptMessage,
    AgentTextMessage,
    TtsAudioMessage,
    TtsStopMessage,
    StateMessage,
    ErrorMessage,
]
