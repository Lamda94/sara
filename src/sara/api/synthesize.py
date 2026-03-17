from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter(tags=["synthesis"])


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "default"


@router.post("/synthesize")
async def synthesize_text(request: SynthesizeRequest):
    """Genera audio a partir de texto (TTS)."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    from sara.services.tts_service import tts_service

    audio_bytes = await tts_service.synthesize(request.text)
    return Response(content=audio_bytes, media_type="audio/wav")
