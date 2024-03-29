from httpx import AsyncClient, Response

from core.settings import settings
from gateways.base import BaseGateway


class BarsicWebGateway(BaseGateway):
    async def get_basis_by_id(self, id: int):
        return await self._client.get(f"api/v1/bases/{id}/", headers=self.clear_headers(self._request.headers))

    async def get_basis_id_in(self, basis_ids: list[int]) -> Response:
        # returns list[BasisRetrieveSchema] from dictionary_service.schemas.basis
        response = await self._client.post(
            "api/v1/bases/list/", json={"bases": basis_ids}, headers=self.clear_headers(self._request.headers)
        )
        return response

    async def get_delivery_destinations_by_ids(self, destination_ids: list[int]) -> Response:
        response = await self._client.post(
            "api/v1/delivery_destinations/list/",
            json={"destination_ids": destination_ids},
            headers=self.clear_headers(self._request.headers),
        )
        return response

    async def get_delivery_destination_by_id(self, id: int) -> Response:
        return await self._client.get(
            f"/api/v1/delivery_destinations/{id}/", headers=self.clear_headers(self._request.headers)
        )

    async def get_acceptance_offset_by_basis_id(self, weekday: int, basis_id: int):
        return await self._client.get(
            "/api/v1/bases/work_schedules/acceptance_offset/",
            params={"weekday": weekday, "basis_id": basis_id},
            headers=self.clear_headers(self._request.headers),
        )


def get_barsic_web_gateway() -> BarsicWebGateway:
    barsic_web_client = AsyncClient(
        base_url=settings.barsic_web_gateway,
        headers={"user-agent": settings.user_agent},
        timeout=300,
    )
    return BarsicWebGateway(client=barsic_web_client, headers={"user-agent": settings.user_agent})
