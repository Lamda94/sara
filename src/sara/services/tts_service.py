import logging
import subprocess
import tempfile
from pathlib import Path

from sara.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Servicio de Text-to-Speech con piper-tts."""

    def __init__(self):
        self.model = settings.tts_model

    async def synthesize(self, text: str) -> bytes:
        """Genera audio WAV a partir de texto."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            cmd = [
                "piper",
                "--model",
                self.model,
                "--output_file",
                tmp.name,
            ]

            result = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )

            if result.returncode != 0:
                error = result.stderr.decode(errors="replace")
                logger.error("piper error: %s", error)
                raise RuntimeError(f"Error al sintetizar audio: {error[:200]}")

            return Path(tmp.name).read_bytes()


tts_service = TTSService()
