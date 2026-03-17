from pydantic import BaseModel


class WSConfigMessage(BaseModel):
    type: str = "config"
    sample_rate: int = 16000
    format: str = "webm"


class WSStatusMessage(BaseModel):
    type: str = "status"
    status: str  # "listening" | "processing" | "speaking"


class WSRecognitionMessage(BaseModel):
    type: str = "recognition"
    user_id: str | None = None
    name: str | None = None
    confidence: float | None = None
    recognized: bool = False


class WSEnrollmentRequest(BaseModel):
    type: str = "enrollment_request"
    message: str = "No te he reconocido. ¿Cómo te llamas?"


class WSTranscriptMessage(BaseModel):
    type: str = "transcript"
    text: str


class WSErrorMessage(BaseModel):
    type: str = "error"
    message: str
