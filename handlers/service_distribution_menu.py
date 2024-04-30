import logging
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from constants import ButtonID, ReportType, button_text
from gateways.client import get_barsic_web_gateway
from states import ServiceDistributionMenu


logger = logging.getLogger(__name__)


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }
    manager.dialog_data["project"] = project


async def get_service_services(report_type: ReportType) -> list[str]:
    gateway = get_barsic_web_gateway()
    response = await gateway.get_new_services(report_type=report_type, db_name="Aquapark_Ulyanovsk")
    return response.json()


async def search_google_report_services(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    text = "Финансовый отчет\nНераспределенные тарифы"
    result = await get_service_services(ReportType.GoogleReport)
    if result:
        await manager.update(
            {
                "report_result": text + ":\n" + "\n".join(result),
            }
        )
    else:
        await manager.update(
            {
                "report_result": text + " не найдены",
            }
        )
    await manager.switch_to(ServiceDistributionMenu.FOUND_SERVICES)


async def search_plat_agent_services(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    text = "Отчет платежного агента\nНераспределенные тарифы"
    result = await get_service_services(ReportType.PlatAgentReport)
    if result:
        await manager.update(
            {
                "report_result": text + ":\n" + "\n".join(result),
            }
        )
    else:
        await manager.update(
            {
                "report_result": text + " не найдены",
            }
        )
    await manager.switch_to(ServiceDistributionMenu.FOUND_SERVICES)


service_distribution_menu = Dialog(
    Window(
        Const("Распределение услуг"),
        Button(
            Const("Поиск новых услуг: Финансовый отчет"),
            id="search_services_google",
            on_click=search_google_report_services,
        ),
        Button(
            Const("Поиск новых услуг: Отчет платежного агента"),
            id="search_services_plat_agent",
            on_click=search_plat_agent_services,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        state=ServiceDistributionMenu.START,
    ),
    Window(
        Format("{dialog_data[report_result]}"),
        state=ServiceDistributionMenu.FOUND_SERVICES,
    ),
    on_start=on_dialog_start,
)
