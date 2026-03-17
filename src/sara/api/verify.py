from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from sara.dependencies import get_db
from sara.schemas.verify import VerifyResponse

router = APIRouter(tags=["verification"])


@router.post("/verify", response_model=VerifyResponse)
async def verify_speaker(
    audio: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    """Verifica la identidad de un hablante por su voz."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo audio")

    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo de audio está vacío")

    from sara.services.speaker_service import speaker_service

    result = await speaker_service.verify(audio_bytes=audio_bytes, db=db)
    return result
