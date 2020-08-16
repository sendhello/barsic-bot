from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, Message

from constants import Button
from misc import dp
from utils import is_correct_command
from .general_commands import GeneralMenu, help_command, set_commands
from .reports_handler import reports_menu_state


@dp.message_handler(state=GeneralMenu.main_menu_state, content_types=ContentTypes.TEXT)
async def general_menu(message: Message, state: FSMContext):  # обратите внимание, есть второй аргумент
    if not await is_correct_command(state, message):
        return

    if message.text == Button.REPORTS:
        await reports_menu_state(message, state)
    elif message.text == Button.HELP:
        await help_command(message)
    elif message.text == Button.SET_COMMANDS:
        await set_commands(message)
