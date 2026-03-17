from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter(tags=["transcription"])


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile,
    language: str = "es",
):
    """Transcribe un archivo de audio a texto."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo audio")

    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="El archivo de audio está vacío")

    from sara.services.stt_service import stt_service

    result = await stt_service.transcribe(audio_bytes, language=language)
    return result
