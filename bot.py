import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message,
    CallbackQuery
)

from callbacks import people_in_zone, total_report
from config import TELEGRAM_TOKEN
from datetime import datetime, timedelta

from library import telegramcalendar

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def inline_keyboard(message: Message):
    people_in_zone_button = InlineKeyboardButton('Люди в зоне', callback_data='people_in_zone')
    reports_button = InlineKeyboardButton('Отчеты', callback_data='reports')
    kb = InlineKeyboardMarkup().add(people_in_zone_button, reports_button)
    await message.answer('Выберите действие', reply_markup=kb)


@dp.message_handler(commands=['help'])
async def process_help_command(message: Message):
    await message.reply('Хееееелп!')


# =================================================== Start ===========================================================
@dp.callback_query_handler(lambda c: c.data == 'people_in_zone')
async def process_people_in_zone(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, await people_in_zone())


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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
