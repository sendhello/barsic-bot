from aiohttp import ClientSession
from bunch import Bunch


async def fetch(url):
    async with ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                return f'Error {r.status}'
            content = await r.json()
    return content


def bbunchify(x):
    if isinstance(x, dict):
        return Bunch((k, bbunchify(v)) for k, v in x.items())
    elif isinstance(x, (list, tuple)):
        return type(x)(bbunchify(v) for v in x)
    else:
        return x
