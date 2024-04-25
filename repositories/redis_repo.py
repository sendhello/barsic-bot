import logging
from datetime import date

from redis.asyncio import Redis

from constants import LIMIT_ID
from core.settings import settings
from db.redis_db import get_redis


logger = logging.getLogger(__name__)


class RedisRepo:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def put_to_cache(self, key: str, data: bytes):
        """Метод записи в кеш."""

        logger.info(f"Writing data to redis: key {key}")
        await self.redis.set(key, data, settings.cache_time)

    async def get_from_cache(self, key: str) -> bytes | None:
        """Метод получения данных из кеша."""

        data = await self.redis.get(key)
        if not data:
            logger.info(f"Data by key {key} not found in redis")
            return None

        logger.info(f"Getting data from redis: key = {key}")
        return data

    async def add_to_set(self, key: str, data: str):
        logger.info(f"Writing data to set of redis: key {key}")
        await self.redis.sadd(key, data)
        await self.redis.expire(key, settings.cache_time)

    async def delete_from_set(self, key: str):
        logger.info(f"Deleting data from set of redis: key {key}")
        await self.redis.srem(key)

    async def check_if_exists(self, key: str, value: str) -> bool:
        logger.info(f"Checking if key {key} exists")
        return bool(await self.redis.sismember(key, value))

    async def is_limit_exceeded(self, user_id: int):
        """Проверка лимита ввода пароля.

        Проверяет сколько вводов пароля за текущие сутки сделал пользователь
        и возвращает True при превышении лимита запросов.

        Если WRITE_PASSWORD_LIMIT_PER_DAY равен 0 - лимит запросов не проверяется
        """
        if settings.password_limit == 0:
            return False

        today = date.today()
        key = f"{LIMIT_ID}:{str(user_id)}:{today}"

        pipe = self.redis.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, 60 * 60 * 24)
        result = await pipe.execute()
        request_number = result[0]
        if request_number > settings.password_limit:
            return True

        return False


async def get_redis_repo() -> RedisRepo:
    redis = await get_redis()
    return RedisRepo(redis)
