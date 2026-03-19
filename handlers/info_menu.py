import logging
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format

from constants import ButtonID, button_text
from gateways.client import get_barsic_web_gateway
from schemas.report import PeopleInZone
from states import InfoMenu

logger = logging.getLogger(__name__)


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }
    manager.dialog_data["project"] = project


async def get_client_count() -> PeopleInZone:
    gateway = get_barsic_web_gateway()
    response = await gateway.client_count()
    return PeopleInZone.model_validate(response.json())


def is_not_people_in_zone(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["info_type"] != "people_in_zone"


async def show_people_in_zone(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    people_in_zone_report = await get_client_count()
    await manager.update(
        {
            "show_data": (
                "Количество людей в зоне\n"
                f"Аквазона: {people_in_zone_report.aquazone}\n"
                f"Всего: {people_in_zone_report.total}"
            ),
        }
    )
    await manager.switch_to(InfoMenu.SHOW_STATE)


info_menu = Dialog(
    Window(
        Const("Инфо"),
        Row(
            Button(
                Const("👥 Люди в зоне"),
                id="people_in_zone",
                on_click=show_people_in_zone,
            ),
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        state=InfoMenu.START,
    ),
    Window(
        Format("{dialog_data[show_data]}"),
        state=InfoMenu.SHOW_STATE,
    ),
    on_start=on_dialog_start,
)
