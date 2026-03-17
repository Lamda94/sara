import uuid
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sara.models.user import User
from sara.models.voice_profile import VoiceProfile

logger = logging.getLogger(__name__)


class UserService:
    """Servicio de gestión de usuarios."""

    async def get_user(self, user_id: uuid.UUID, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_profiles(self, user_id: uuid.UUID, db: AsyncSession) -> list[VoiceProfile]:
        result = await db.execute(
            select(VoiceProfile)
            .where(VoiceProfile.user_id == user_id)
            .where(VoiceProfile.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def delete_user(self, user_id: uuid.UUID, db: AsyncSession) -> bool:
        user = await self.get_user(user_id, db)
        if not user:
            return False
        await db.delete(user)
        await db.commit()
        logger.info("Usuario eliminado: %s (id=%s)", user.name, user.id)
        return True


user_service = UserService()
