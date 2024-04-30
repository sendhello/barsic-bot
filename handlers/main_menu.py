import logging
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, DialogProtocol, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const, Format

from constants import ADMIN_KEY, BLOCKED_USER_ID, PERMISSION_ID, USER_KEY
from core.settings import settings
from repositories.redis_repo import get_redis_repo
from states import InfoMenu, MainMenu, ReportMenu, ServiceDistributionMenu


logger = logging.getLogger(__name__)


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }
    manager.dialog_data["project"] = project
    if isinstance(start_data, dict):
        manager.dialog_data["permission"] = start_data.get("permission")


async def get_password(message: Message, dialog: DialogProtocol, manager: DialogManager) -> None:
    redis_repo = await get_redis_repo()
    user_id = message.from_user.id

    if message.text == settings.admin_password.get_secret_value():
        await redis_repo.put_to_cache(key=f"{PERMISSION_ID}:{user_id}", data=ADMIN_KEY)
        manager.dialog_data["permission"] = ADMIN_KEY
        await manager.next()
        return None

    if message.text == settings.user_password.get_secret_value():
        await redis_repo.put_to_cache(key=f"{PERMISSION_ID}:{user_id}", data=USER_KEY)
        manager.dialog_data["permission"] = USER_KEY
        await manager.next()
        return None

    if await redis_repo.is_limit_exceeded(user_id):
        await message.answer("Превышено количество попыток ввода пароля. Пользователь заблокирован.")
        await redis_repo.add_to_set(key=f"{BLOCKED_USER_ID}", data=str(user_id))


def is_admin(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    logger.warning(f"TEMP: {is_admin}")
    return data["dialog_data"]["permission"] in [ADMIN_KEY]


def is_user_or_admin(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    logger.warning(f"TEMP: {is_user_or_admin}")
    return data["dialog_data"]["permission"] in [ADMIN_KEY, USER_KEY]


async def logout(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    redis_repo = await get_redis_repo()
    user_id = callback.from_user.id
    await redis_repo.del_from_cache(f"{PERMISSION_ID}:{user_id}")
    await manager.start(MainMenu.AUTHORIZATION)


main_menu = Dialog(
    Window(
        Format("Здравствуйте, {event.from_user.username}! \n\n" "Введите пароль\n"),
        MessageInput(get_password),
        state=MainMenu.AUTHORIZATION,
    ),
    Window(
        Format("Здравствуйте, {event.from_user.username}! \n\n" "Выберите действие\n"),
        Start(
            Const("ℹ️ Инфо"),
            id="info",
            state=InfoMenu.START,
            when=is_user_or_admin,
        ),
        Start(
            Const("⚙️ Генерация отчетов"),
            id="report",
            state=ReportMenu.START,
            when=is_admin,
        ),
        Start(
            Const("🏗️ Распределение услуг"),
            id="services_distribution",
            state=ServiceDistributionMenu.START,
            when=is_admin,
        ),
        Button(
            Const("🚪 Выйти"),
            id="build_report",
            on_click=logout,
        ),
        state=MainMenu.START,
    ),
    on_start=on_dialog_start,
)
