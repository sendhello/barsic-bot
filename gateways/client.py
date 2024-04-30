import logging
from datetime import date, datetime, timedelta

from httpx import AsyncClient, HTTPError, Response

from constants import ReportType
from core.settings import settings
from gateways.base import BaseGateway


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

    async def get_new_services(self, report_type: ReportType, db_name: str) -> Response:
        response = await self.get(
            url="/api/v1/report_settings/new_services",
            params={
                "report_name": report_type.value,
                "db_name": db_name,
            },
        )
        logger.info(f"Response: {response.json()}")
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
