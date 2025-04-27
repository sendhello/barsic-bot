import logging
from datetime import date, datetime, timedelta
from uuid import UUID

import orjson
from httpx import AsyncClient, HTTPError, Response

from constants import ReportType
from core.settings import settings
from gateways.base import BaseGateway
from schemas.report import ServicesGroup


logger = logging.getLogger(__name__)


class BarsicWebGateway(BaseGateway):

    async def client_count(self) -> Response:
        return await self.post(url="/api/v1/reports/client_count")

    async def create_reports(
        self, start_date: date, end_date: date, use_yadisk: bool, telegram_report: bool
    ) -> Response:
        return await self.post(
            url="/api/v1/reports/create_reports",
            params={
                "date_from": datetime.combine(start_date, datetime.min.time()),
                "date_to": datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                "use_yadisk": use_yadisk,
                "telegram_report": telegram_report,
            },
        )

    async def create_total_report_by_day(
        self, start_date: date, end_date: date, use_cache: bool, db_name: str
    ) -> Response:
        return await self.post(
            url="/api/v1/reports/create_total_report_by_day",
            params={
                "date_from": datetime.combine(start_date, datetime.min.time()),
                "date_to": datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                "use_cache": use_cache,
                "db_name": db_name,
            },
        )

    async def create_purchased_goods_report(
        self, start_date: date, end_date: date, goods: list[str], use_yadisk: bool, hide_zero: bool, db_name: str
    ) -> Response:
        return await self.post(
            url="/api/v1/reports/create_purchased_goods_report",
            params={
                "date_from": datetime.combine(start_date, datetime.min.time()),
                "date_to": datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
                "goods": goods,
                "save_to_yandex": use_yadisk,
                "hide_zero": hide_zero,
                "db_name": db_name,
            },
        )

    async def get_new_services(self, report_type: ReportType, db_name: str) -> Response:
        response = await self.get(
            url="/api/v1/report_settings/new_services",
            params={
                "report_name": report_type.value,
                "db_name": db_name,
            },
        )
        logger.debug(f"Response: {response.json()}")
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(e)

        return response

    async def get_services_groups(self, report_type: ReportType) -> Response:
        response = await self.get(url="/api/v1/report_name/", params={"report_name": report_type.value})
        logger.debug(f"Response: {response.json()}")
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(e)

        services_groups = [ServicesGroup(**raw) for raw in response.json()]
        if not services_groups:
            raise HTTPError(f"Report type with name '{report_type}' not found")

        response = await self.get(url="/api/v1/report_group/", params={"report_name_id": response.json()[0]["id"]})
        logger.debug(f"Response: {response.json()}")
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(e)

        return response

    async def get_service_elements(self, report_group_id: UUID) -> Response:
        response = await self.get(url="/api/v1/report_element/", params={"report_group_id": report_group_id})
        logger.debug(f"Response: {response.json()}")
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(e)

        return response

    async def add_service_element(self, group_id: UUID, new_elements: list[str]) -> Response:
        response = await self.post(
            url=f"/api/v1/report_group/{str(group_id)}/add_elements/",
            data=orjson.dumps(new_elements),
        )
        logger.debug(f"Response: {response.json()}")
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(e)

        return response

    async def delete_service_element(self, service_element_id: UUID) -> Response:
        response = await self.delete(url=f"/api/v1/report_element/{str(service_element_id)}")
        logger.debug(f"Response: {response.json()}")
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.exception(e)

        return response


def get_barsic_web_gateway() -> BarsicWebGateway:
    barsic_web_client = AsyncClient(
        base_url=settings.barsic_web_gateway,
        headers={"user-agent": settings.user_agent},
        timeout=300,
    )
    return BarsicWebGateway(client=barsic_web_client, headers={"user-agent": settings.user_agent})
