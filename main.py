from aiogram import Bot, Dispatcher, executor, types
from uvloop import loop
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import ujson
import emoji
import logging
import yaml
from helpers import bbunchify
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from datetime import datetime, timedelta


with open('config.yaml') as f:
    config = bbunchify(yaml.safe_load(f))

TELEGRAM_TOKEN = config.general.telegram_token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['keyboard'])
async def cmd_start(message: types.Message):
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    poll_keyboard.row(KeyboardButton('Люди в зоне'), KeyboardButton('Отчеты'), KeyboardButton('Отмена'))
    poll_keyboard.add(KeyboardButton('Отправить свой контакт ☎️', request_contact=True),
                      KeyboardButton('Отправить свою локацию 🗺️', request_location=True)
                      )
    poll_keyboard.add(KeyboardButton('Отмена'))
    await message.answer("Выберите период отчета", reply_markup=poll_keyboard)


@dp.message_handler(lambda message: message.text == "Отмена")
async def action_cancel(message: types.Message):
    await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands='start')
async def inline_keyboard(message: types.Message):
    people_in_zone_button = InlineKeyboardButton('Люди в зоне', callback_data='people_in_zone')
    reports_button = InlineKeyboardButton('Отчеты', callback_data='reports')
    kb = InlineKeyboardMarkup().add(people_in_zone_button, reports_button)
    await message.answer('Выберите действие', reply_markup=kb)


async def fetch(url):
    async with ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                return f'Error {r.status}'
            content = await r.json()
    return content


async def total_report():
    url = 'http://localhost:8000/api/v1.0/total_report/'
    params = {
        'db_type': 'aqua',
        'company_id': '36',
        'date_from': datetime.now().strftime('%Y%m%d'),
        'date_to': (datetime.now() - timedelta(weeks=15)).strftime('%Y%m%d')
    }
    try:
        response = await fetch(url, params=params)
    except ClientConnectorError:
        return 'Сервер не доступен'
    if response['status'] != 'ok':
        return f"Errors: {response['errors']}"
    result = 'Люди в зоне:\n'
    for zone_name, people in response['data']['report'].items():
        result += f'{zone_name}: {people}\n'
    return result


async def people_in_zone():
    url = 'http://localhost:8000/api/v1.0/people-in-zone/'
    try:
        response = await fetch(url)
    except ClientConnectorError:
        return 'Сервер не доступен'
    if response['status'] != 'ok':
        return f"Errors: {response['errors']}"
    result = 'Люди в зоне:\n'
    for zone_name, people in response['data']['report'].items():
        result += f'{zone_name}: {people}\n'
    return result


@dp.callback_query_handler(lambda c: c.data == 'people_in_zone')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, await people_in_zone())


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply('Хееееелп!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)