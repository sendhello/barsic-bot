from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from constants import BLOCKED_USER_ID
from repositories.redis_repo import get_redis_repo


class BlockerUserMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[Message, dict[str, Any]], Awaitable[Any]], event: Message, data: dict[str, Any]
    ) -> Any:
        redis_repo = await get_redis_repo()
        user_id = event.from_user.id

        if await redis_repo.check_if_exists(BLOCKED_USER_ID, str(user_id)):
            return None

        return await handler(event, data)
