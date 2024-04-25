import logging

from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, DialogProtocol, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Start
from aiogram_dialog.widgets.text import Const, Format

from constants import ADMIN_KEY, BLOCKED_USER_ID, PERMISSION_ID, USER_KEY, ButtonID, text
from core.settings import settings
from repositories.redis_repo import get_redis_repo
from states import MainMenu, ReportMenu


logger = logging.getLogger(__name__)


async def get_password(message: Message, dialog: DialogProtocol, manager: DialogManager):
    redis_repo = await get_redis_repo()
    user_id = message.from_user.id

    if message.text == settings.admin_password.get_secret_value():
        await redis_repo.put_to_cache(key=f"{PERMISSION_ID}:{user_id}", data=ADMIN_KEY)
        await manager.next()

    if message.text == settings.user_password.get_secret_value():
        await redis_repo.put_to_cache(key=f"{PERMISSION_ID}:{user_id}", data=USER_KEY)
        await manager.next()

    if await redis_repo.is_limit_exceeded(user_id):
        await message.answer("Превышено количество попыток ввода пароля. Пользователь заблокирован.")
        await redis_repo.add_to_set(key=f"{BLOCKED_USER_ID}", data=str(user_id))


main_menu = Dialog(
    Window(
        Format("Здравствуйте, {event.from_user.username}! \n\n" "Введите пароль\n"),
        MessageInput(get_password),
        state=MainMenu.AUTHORIZATION,
    ),
    Window(
        Format("Здравствуйте, {event.from_user.username}! \n\n" "Выберите действие\n"),
        Row(
            Start(
                Const(text(ButtonID.REPORTS)),
                id="main",
                state=ReportMenu.START,
            )
        ),
        state=MainMenu.START,
    ),
)
