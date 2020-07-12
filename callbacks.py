from datetime import datetime, timedelta

from aiohttp.client_exceptions import ClientConnectorError

from utils import fetch


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
        return f"Ошибка запроса: {response['errors']}"
    result = 'Люди в зоне:\n'
    for zone_name, people in response['data']['report'].items():
        result += f'{zone_name}: {people}\n'
    return result
