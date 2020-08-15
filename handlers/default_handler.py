from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentTypes, Message

from callbacks import people_in_zone, total_report
from library import telegramcalendar
from misc import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from .general_commands import GeneralMenu, help_command, set_commands
from .reports_handler import reports_menu_state
from utils import is_correct_command


@dp.message_handler(state=GeneralMenu.main_menu_state, content_types=ContentTypes.TEXT)
async def general_menu(message: Message, state: FSMContext):  # обратите внимание, есть второй аргумент
    if not await is_correct_command(state, message):
        return

    if message.text.lower() == 'отчеты':
        await reports_menu_state(message, state)
    elif message.text.lower() == 'помощь':
        await help_command(message)
    elif message.text.lower() == 'установить команды':
        await set_commands(message)
