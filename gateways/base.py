from abc import ABC
from functools import partial
from typing import Callable, Mapping, ParamSpec, Type, TypeVar

import pydantic
from httpx import AsyncClient, Response

P = ParamSpec("P")
T = TypeVar("T")


def create_partial(func: Callable[P, T], *args, **kwargs) -> Callable[P, T]:
    """
    Создание partial c работающим type-hinting для разработки
    """
    return partial(func, *args, **kwargs)


class BaseGateway(ABC):
    def __init__(self, client: AsyncClient, headers: Mapping[str, str]):
        self._client = client
        self.headers = self.clear_headers(headers)

        # Шорткаты подставляющие хедеры.
        # Хедеры можно переопределять, старые не будут отправляться
        # Если нужно добавить/удалить хедер - нужно добавлять/удалять напрямую в self.headers
        self.post = create_partial(self._client.post, headers=self.headers)
        self.get = create_partial(self._client.get, headers=self.headers)
        self.put = create_partial(self._client.put, headers=self.headers)
        self.patch = create_partial(self._client.patch, headers=self.headers)
        self.delete = create_partial(self._client.delete, headers=self.headers)
        self.options = create_partial(self._client.options, headers=self.headers)

    @staticmethod
    def clear_params(params: dict) -> dict:
        return {k: v for k, v in params.items() if v}

    @staticmethod
    def clear_headers(headers: Mapping[str, str]) -> dict:
        not_allowed_headers = ("content-length", "host", "content-type", "user-agent")
        headers = dict(headers)
        return {k: v for k, v in headers.items() if k.lower() not in not_allowed_headers}

    async def close(self):
        await self._client.aclose()

    @staticmethod
    def parse_response_as(schema: Type[T], response: Response) -> T:
        response.raise_for_status()
        return pydantic.TypeAdapter.validate_python(schema, response.json())
