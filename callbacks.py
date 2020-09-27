from datetime import datetime, timedelta

from aiohttp.client_exceptions import ClientConnectorError

from utils import fetch
from config import API_URI


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
