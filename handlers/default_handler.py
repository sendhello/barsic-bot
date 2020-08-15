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


@dp.callback_query_handler(lambda c: c.data == 'people_in_zone')
async def process_people_in_zone(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, text=await people_in_zone())


@dp.callback_query_handler(lambda c: c.data == 'reports')
async def process_reports(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    short_report_button = InlineKeyboardButton('Краткий', callback_data='short_report')
    sum_report_button = InlineKeyboardButton('Суммовой', callback_data='sum_report')
    total_report_button = InlineKeyboardButton('Итоговый', callback_data='total_report')
    kb = InlineKeyboardMarkup().add(short_report_button, sum_report_button, total_report_button)
    await bot.send_message(callback_query.from_user.id, 'Какой отчет хотите получить?', reply_markup=kb)


# =================================================== Отчеты ===========================================================
@dp.callback_query_handler(lambda c: c.data == 'short_report')
async def process_short_report(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, await short_report())


@dp.callback_query_handler(lambda c: c.data == 'sum_report')
async def process_sum_report(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, await sum_report())


@dp.callback_query_handler(lambda c: c.data == 'total_report')
async def process_total_report(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    run_request = InlineKeyboardButton('Запрос', callback_data='run_request')
    change = InlineKeyboardButton('Изменить', callback_data='change')
    kb = InlineKeyboardMarkup().add(run_request, change)
    await bot.send_message(callback_query.from_user.id, 'Итоговый отчет за ...', reply_markup=kb)


# =============================================== Итоговый отчет =======================================================
@dp.callback_query_handler(lambda c: c.data == 'run_request')
async def process_total_report_run_request(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, await total_report(
        date_from=datetime(year=2020, month=1, day=1), date_to=datetime(year=2020, month=1, day=2)))


@dp.callback_query_handler(lambda c: c.data == 'change')
async def process_total_report_run_request(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, text='От', reply_markup=telegramcalendar.create_calendar())