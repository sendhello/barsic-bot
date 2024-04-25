import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from constants import PERMISSION_ID
from repositories.redis_repo import get_redis_repo


logger = logging.getLogger(__name__)


class PermissionFilter(BaseFilter):
    def __init__(self, roles: list[str]) -> None:
        self.roles = roles

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        redis_repo = await get_redis_repo()
        permission = await redis_repo.get_from_cache(key=f"{PERMISSION_ID}:{user_id}")
        if permission is None:
            return False

        if permission not in self.roles:
            return False

        return True
