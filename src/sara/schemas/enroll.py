import uuid

from pydantic import BaseModel


class EnrollResponse(BaseModel):
    user_id: uuid.UUID
    name: str
    quality_score: float | None = None
    message: str
