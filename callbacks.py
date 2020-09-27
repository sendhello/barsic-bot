from datetime import datetime
from aiogram.types import CallbackQuery, Message
from aiohttp.client_exceptions import ClientConnectorError

from config import API_URI
from library.aiogramcalendar import calendar_callback, process_calendar_selection, create_calendar
from misc import dp
from utils import fetch

from states import ReportsStates

from aiogram.dispatcher import FSMContext
from constants import Button


@dp.callback_query_handler(calendar_callback.filter(), state=ReportsStates.choose_date_from_state)
@dp.callback_query_handler(calendar_callback.filter(), state=ReportsStates.choose_date_to_state)
async def calendar_process(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await process_calendar_selection(callback_query, callback_data)
    if selected:
        if await state.get_state() == 'ReportsStates:choose_date_from_state':
            await ReportsStates.choose_date_to_state.set()
            await state.update_data(date_from=date.strftime('%Y%m%d'))
            await callback_query.message.answer(f'Начало периода: {date.strftime("%d-%m-%Y")}')
            await callback_query.message.answer("Выберите конец периода: ", reply_markup=create_calendar())
        else:
            await state.update_data(date_to=date.strftime('%Y%m%d'))
            await callback_query.message.answer(f'Конец периода: {date.strftime("%d-%m-%Y")}')

            # Генерируем новое сообщение из копии сохраненной в памяти и переходим с ним на другой стейт
            from handlers.reports_handler import set_period_state
            memory = await state.get_data()
            message = memory['message']
            message.text = Button.SET
            await set_period_state(message=message, state=state)


async def people_in_zone():
    url = f'{API_URI}/people-in-zone/'
    params = {
        'db_type': 'aqua'
    }

    try:
        response = await fetch(url, params)
    except ClientConnectorError:
        return 'Сервер не доступен'

    if response['status'] != 'ok':
        return f"Ошибка запроса: {response['errors']}"

    result = 'Люди в зоне:\n'
    for zone_name, people in response['data']['report'].items():
        result += f'{zone_name}: {people}\n'
    return result


async def total_report(date_from: datetime, date_to: datetime):
    url = f'{API_URI}/total-report/'
    params = {
        'db_type': 'aqua',
        'company_id': '36',
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d')
    }
    try:
        response = await fetch(url, params)
    except ClientConnectorError:
        return 'Сервер не доступен'

    if response['status'] != 'ok':
        return f"Ошибка запроса: {response.get('errors')}"

    result = response['data']['report']
    return result


async def cash_report(date_from: datetime, date_to: datetime):
    url = f'{API_URI}/cash-report/'
    params = {
        'db_type': 'aqua',
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d')
    }
    try:
        response = await fetch(url, params)
    except ClientConnectorError:
        return 'Сервер не доступен'

    if response['status'] != 'ok':
        return f"Ошибка запроса: {response.get('errors')}"

    result = response['data']['report']
    return result
