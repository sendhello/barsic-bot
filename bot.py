import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message,
    CallbackQuery
)

from callbacks import people_in_zone
from config import TELEGRAM_TOKEN

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


@dp.callback_query_handler(lambda c: c.data == 'people_in_zone')
async def process_callback_button1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, await people_in_zone())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
