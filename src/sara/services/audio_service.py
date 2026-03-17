import logging
import subprocess
import tempfile
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


class AudioService:
    """Servicio de conversion y preprocesamiento de audio."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    async def convert_to_wav(self, audio_bytes: bytes) -> bytes:
        """Convierte audio de cualquier formato a WAV 16kHz mono."""
        with (
            tempfile.NamedTemporaryFile(suffix=".input", delete=True) as inp,
            tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as out,
        ):
            inp.write(audio_bytes)
            inp.flush()

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                inp.name,
                "-ar",
                str(self.sample_rate),
                "-ac",
                "1",
                "-f",
                "wav",
                out.name,
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode != 0:
                error = result.stderr.decode(errors="replace")
                logger.error("ffmpeg error: %s", error)
                raise RuntimeError(f"Error al convertir audio: {error[:200]}")

            return Path(out.name).read_bytes()

    def wav_to_numpy(self, wav_bytes: bytes) -> np.ndarray:
        """Convierte WAV bytes a numpy array float32 normalizado."""
        # Saltar header WAV (44 bytes) y leer PCM 16-bit
        pcm_data = np.frombuffer(wav_bytes[44:], dtype=np.int16)
        return pcm_data.astype(np.float32) / 32768.0

    def get_duration_seconds(self, wav_bytes: bytes) -> float:
        """Obtiene la duracion en segundos de un WAV."""
        samples = (len(wav_bytes) - 44) // 2
        return samples / self.sample_rate

    def assess_quality(self, wav_bytes: bytes) -> dict:
        """Evalua la calidad del audio (duracion, SNR estimado)."""
        audio = self.wav_to_numpy(wav_bytes)
        duration = len(audio) / self.sample_rate

        # SNR estimado simple: ratio señal/ruido
        rms = np.sqrt(np.mean(audio**2))
        snr_estimate = 20 * np.log10(rms + 1e-10)

        return {
            "duration": duration,
            "rms": float(rms),
            "snr_estimate": float(snr_estimate),
            "score": min(1.0, max(0.0, (snr_estimate + 60) / 60)),
        }


audio_service = AudioService()
