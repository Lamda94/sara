import logging
import tempfile

from sara.config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Servicio de Speech-to-Text con faster-whisper."""

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info(
                "Cargando modelo Whisper '%s' en dispositivo '%s'...",
                settings.whisper_model,
                settings.whisper_device,
            )
            self._model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type="int8",
            )
            logger.info("Modelo Whisper cargado correctamente")

    async def transcribe(self, audio_bytes: bytes, language: str | None = None) -> dict:
        """Transcribe audio WAV a texto."""
        self._load_model()

        lang = language or settings.whisper_language

        # Escribir audio a archivo temporal para faster-whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()

            segments, info = self._model.transcribe(
                tmp.name,
                language=lang,
                beam_size=5,
                vad_filter=True,
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            full_text = " ".join(text_parts)

        return {
            "text": full_text,
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
        }


stt_service = STTService()
