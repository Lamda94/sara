from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from sara.dependencies import get_db
from sara.schemas.enroll import EnrollResponse

router = APIRouter(tags=["enrollment"])


@router.post("/enroll", response_model=EnrollResponse)
async def enroll_speaker(
    name: str = Form(...),
    audio: UploadFile = ...,
    db: AsyncSession = Depends(get_db),
):
    """Registra un nuevo usuario con su perfil de voz."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo audio")

    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo de audio está vacío")

    from sara.services.speaker_service import speaker_service

    result = await speaker_service.enroll(
        audio_bytes=audio_bytes,
        name=name.strip(),
        db=db,
    )
    return result
