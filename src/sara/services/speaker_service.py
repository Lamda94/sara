import logging
from datetime import datetime, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sara.config import settings
from sara.models.user import User
from sara.models.voice_profile import VoiceProfile
from sara.schemas.enroll import EnrollResponse
from sara.schemas.verify import VerifyResponse
from sara.services.audio_service import audio_service

logger = logging.getLogger(__name__)


class SpeakerService:
    """Servicio de reconocimiento de hablante con SpeechBrain ECAPA-TDNN."""

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            from speechbrain.inference.speaker import EncoderClassifier

            logger.info("Cargando modelo SpeechBrain ECAPA-TDNN...")
            self._model = EncoderClassifier.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="models/speechbrain",
            )
            logger.info("Modelo SpeechBrain cargado correctamente")

    def extract_embedding(self, wav_bytes: bytes) -> np.ndarray:
        """Extrae el embedding de voz (192-d) de un audio WAV."""
        import torch

        self._load_model()

        audio_np = audio_service.wav_to_numpy(wav_bytes)
        waveform = torch.tensor(audio_np).unsqueeze(0)

        embedding = self._model.encode_batch(waveform)
        return embedding.squeeze().cpu().numpy()

    async def verify(self, audio_bytes: bytes, db: AsyncSession) -> VerifyResponse:
        """Verifica si el hablante es reconocido en la BD."""
        # Asegurar formato WAV
        if not audio_bytes[:4] == b"RIFF":
            audio_bytes = await audio_service.convert_to_wav(audio_bytes)

        # Validar duración mínima
        duration = audio_service.get_duration_seconds(audio_bytes)
        if duration < settings.audio_min_duration_seconds:
            return VerifyResponse(recognized=False)

        # Extraer embedding
        embedding = self.extract_embedding(audio_bytes)
        embedding_list = embedding.tolist()

        # Buscar match con pgvector (similitud coseno)
        result = await db.execute(
            select(
                User,
                VoiceProfile,
                (1 - VoiceProfile.embedding.cosine_distance(embedding_list)).label("similarity"),
            )
            .join(User, VoiceProfile.user_id == User.id)
            .where(VoiceProfile.is_active.is_(True))
            .order_by(VoiceProfile.embedding.cosine_distance(embedding_list))
            .limit(1)
        )

        best_match = result.first()

        if best_match and best_match.similarity >= settings.speaker_similarity_threshold:
            user = best_match.User
            user.last_seen_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(
                "Hablante reconocido: %s (confianza: %.3f)",
                user.name,
                best_match.similarity,
            )
            return VerifyResponse(
                recognized=True,
                user_id=user.id,
                name=user.name,
                confidence=best_match.similarity,
            )

        logger.info("Hablante no reconocido")
        return VerifyResponse(recognized=False)

    async def enroll(self, audio_bytes: bytes, name: str, db: AsyncSession) -> EnrollResponse:
        """Registra un nuevo usuario con su perfil de voz."""
        # Asegurar formato WAV
        if not audio_bytes[:4] == b"RIFF":
            audio_bytes = await audio_service.convert_to_wav(audio_bytes)

        # Validar duración
        duration = audio_service.get_duration_seconds(audio_bytes)
        if duration < settings.audio_min_duration_seconds:
            raise ValueError(
                f"Audio demasiado corto ({duration:.1f}s). "
                f"Se necesitan al menos {settings.audio_min_duration_seconds}s."
            )

        # Evaluar calidad
        quality = audio_service.assess_quality(audio_bytes)

        # Extraer embedding
        embedding = self.extract_embedding(audio_bytes)
        embedding_list = embedding.tolist()

        # Verificar que no sea un usuario ya existente
        existing = await self.verify(audio_bytes, db)
        if existing.recognized:
            raise ValueError(
                f"Esta voz ya está registrada como '{existing.name}' "
                f"(confianza: {existing.confidence:.2f})"
            )

        # Crear usuario y perfil
        user = User(name=name)
        db.add(user)
        await db.flush()

        profile = VoiceProfile(
            user_id=user.id,
            embedding=embedding_list,
            audio_quality_score=quality["score"],
        )
        db.add(profile)
        await db.commit()

        logger.info("Nuevo usuario registrado: %s (id=%s)", name, user.id)

        return EnrollResponse(
            user_id=user.id,
            name=name,
            quality_score=quality["score"],
            message=f"Usuario '{name}' registrado correctamente.",
        )


speaker_service = SpeakerService()
