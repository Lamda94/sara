import uuid

from pydantic import BaseModel


class VerifyResponse(BaseModel):
    recognized: bool
    user_id: uuid.UUID | None = None
    name: str | None = None
    confidence: float | None = None
