import logging
from enum import Enum
from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from constants import ButtonID, button_text
from gateways.client import get_barsic_web_gateway
from states import ServiceDistributionMenu


logger = logging.getLogger(__name__)

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")


class ReportType(str, Enum):
    GoogleReport = "GoogleReport"
    PlatAgentReport = "PlatAgentReport"
    ItogReport = "ItogReport"


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }
    manager.dialog_data["project"] = project


async def get_service_services(report_type: ReportType) -> list[str]:
    gateway = get_barsic_web_gateway()
    response = await gateway.post(
        url="/api/v1/report_settings/new_services",
        params={
            "report_name": report_type,
            "db_name": "Aquapark_Ulyanovsk",
        },
    )
    return response.json()


async def search_google_report_services(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    result = await get_service_services(ReportType.GoogleReport)
    await manager.update(
        {
            "report_result": ("Нераспределенные тарифы:\n" "\n".join(result)),
        }
    )
    await manager.switch_to(ServiceDistributionMenu.FOUND_SERVICES)


async def search_plat_agent_services(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    result = await get_service_services(ReportType.GoogleReport)
    await manager.update(
        {
            "report_result": ("Нераспределенные тарифы:\n" "\n".join(result)),
        }
    )
    await manager.switch_to(ServiceDistributionMenu.FOUND_SERVICES)


report_menu = Dialog(
    Window(
        Const("Распределение услуг"),
        Button(
            Const(f"Поиск новых услуг {ReportType.GoogleReport}"),
            id="search_services_google",
            on_click=search_google_report_services,
        ),
        Button(
            Const(f"Поиск новых услуг {ReportType.PlatAgentReport}"),
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
