import asyncio
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.filters.command import BotCommand
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from constants import ButtonID, text
from core.settings import settings
from db import redis_db
from handlers import router


async def setup_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description=text(ButtonID.START)),
        BotCommand(command="/help", description=text(ButtonID.HELP)),
    ]
    await bot.set_my_commands(commands)


@asynccontextmanager
async def lifespan():
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True)
    yield

    await redis_db.redis.close()


# Запуск бота
async def main():
    bot = Bot(token=settings.bot_telegram_token.get_secret_value())
    await setup_commands(bot)
    dp = Dispatcher()
    dp.include_router(router)
    setup_dialogs(dp)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    async with lifespan():
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
