from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://sara:sara_dev_password@localhost:5432/sara"

    # Whisper STT
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    whisper_language: str = "es"

    # Speaker recognition
    speaker_similarity_threshold: float = 0.75
    speaker_embedding_dim: int = 192

    # TTS
    tts_model: str = "es_ES-davefx-medium"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # Audio
    audio_sample_rate: int = 16000
    audio_max_duration_seconds: int = 30
    audio_min_duration_seconds: float = 1.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
