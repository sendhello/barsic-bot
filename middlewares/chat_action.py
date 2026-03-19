from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from aiogram.utils.chat_action import ChatActionSender


class ChatActionMiddleware(BaseMiddleware):
    def __init__(self, default_action: str = "typing", initial_sleep: float = 1.0):
        self.default_action = default_action
        self.initial_sleep = initial_sleep

    @staticmethod
    def _extract_chat_id(event: TelegramObject) -> int | None:
        chat = getattr(event, "chat", None)
        if chat is not None:
            return chat.id

        message = getattr(event, "message", None)
        if message is not None:
            message_chat = getattr(message, "chat", None)
            if message_chat is not None:
                return message_chat.id

        return None

    @staticmethod
    def _extract_bot(event: TelegramObject, data: dict[str, Any]) -> Bot | None:
        bot = data.get("bot")
        if bot is not None:
            return bot

        event_bot = getattr(event, "bot", None)
        if event_bot is not None:
            return event_bot

        message = getattr(event, "message", None)
        if message is not None:
            message_bot = getattr(message, "bot", None)
            if message_bot is not None:
                return message_bot

        return None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat_id = self._extract_chat_id(event)
        bot = self._extract_bot(event, data)
        if chat_id is None or bot is None:
            return await handler(event, data)

        action = get_flag(data, "long_operation") or self.default_action
        async with ChatActionSender(bot=bot, action=action, chat_id=chat_id, initial_sleep=self.initial_sleep):
            return await handler(event, data)
