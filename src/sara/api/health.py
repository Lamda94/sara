from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "sara", "version": "0.1.0"}


@router.get("/info")
async def info():
    from sara.config import settings

    return {
        "service": "sara",
        "version": "0.1.0",
        "whisper_model": settings.whisper_model,
        "speaker_embedding_dim": settings.speaker_embedding_dim,
        "similarity_threshold": settings.speaker_similarity_threshold,
    }
