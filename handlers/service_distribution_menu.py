import logging
import operator
from copy import deepcopy
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Checkbox, Column, ManagedCheckbox, Radio
from aiogram_dialog.widgets.kbd.select import ManagedRadio
from aiogram_dialog.widgets.text import Const, Format

from constants import REPORT_NAME_MAP, ButtonID, ReportType, button_text
from core.settings import settings
from gateways.client import get_barsic_web_gateway
from schemas.report import ReportElement, ServicesGroup
from states import ServiceDistributionMenu


logger = logging.getLogger(__name__)


# async def next_page_handler(
#     callback: CallbackQuery,
#     button: Button,
#     manager: DialogManager,
# ):
#     await manager.switch_to(state=getattr(ServiceDistributionMenu, f"DISTRIBUTION_ELEMENTS_2"))
#
#
# async def back_page_handler(
#     callback: CallbackQuery,
#     button: Button,
#     manager: DialogManager,
# ):
#     await manager.back()
#     await manager.next()
#
#
# async def first_page_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.back()
#     await manager.next()
#
#
# async def last_page_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
#     await manager.back()
#     await manager.next()


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }
    manager.dialog_data["project"] = project
    manager.dialog_data["checked_elements"] = []


async def start_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await manager.update({"report_type": button.widget_id})
    await manager.switch_to(ServiceDistributionMenu.REPORT_MENU)


async def search_new_services_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    report_map = {
        "finance_report": ReportType.GoogleReport,
        "total_by_day": ReportType.PlatAgentReport,
    }
    report_type = report_map[manager.dialog_data["report_type"]]
    report_name = REPORT_NAME_MAP[manager.dialog_data["report_type"]]
    gateway = get_barsic_web_gateway()

    response = await gateway.get_new_services(report_type=report_type, db_name="Aquapark_Ulyanovsk")
    result = response.json()
    if result:
        await manager.update(
            {
                "new_elements": result[:50],  # Отдаем не более 50 кнопок одновременно
            }
        )
        await manager.switch_to(ServiceDistributionMenu.DISTRIBUTION_ELEMENTS)
    else:
        await manager.update(
            {
                "result_text": f"{report_name}\nНераспределенные тарифы не найдены",
            }
        )
        await manager.switch_to(ServiceDistributionMenu.END)


async def view_services_groups_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    gateway = get_barsic_web_gateway()
    report_map = {
        "finance_report": ReportType.GoogleReport,
        "total_by_day": ReportType.PlatAgentReport,
    }
    report_type = report_map[manager.dialog_data["report_type"]]
    response = await gateway.get_services_groups(report_type=report_type)
    services_groups = [ServicesGroup.model_validate(raw) for raw in response.json()]
    await manager.update(
        {
            "services_groups": services_groups,
        }
    )
    await manager.switch_to(ServiceDistributionMenu.SERVICES_GROUPS)


async def services_groups_radio_handler(
    event: CallbackQuery,
    select: ManagedRadio,
    dialog_manager: DialogManager,
    data: Any,
):
    gateway = get_barsic_web_gateway()

    services_group = None
    for group in dialog_manager.dialog_data["services_groups"]:
        if str(group.id) == str(data):
            services_group = group.title

    response = await gateway.get_service_elements(report_group_id=data)
    elements = [ReportElement.model_validate(raw) for raw in response.json()]
    await dialog_manager.update(
        {
            "elements": elements,
            "services_group": services_group,
        }
    )
    await dialog_manager.switch_to(ServiceDistributionMenu.SERVICES_GROUP_ELEMENTS)


async def new_element_checkbox_handler(
    event: CallbackQuery,
    checkbox: ManagedCheckbox,
    manager: DialogManager,
):
    data = manager.dialog_data
    pos = int(checkbox.widget.widget_id.split("_")[-1])
    element = data["new_elements"][pos]
    if checkbox.is_checked():
        data["checked_elements"].remove(element)
        logger.info(f"Element {element} unchecked")
    else:
        data["checked_elements"].append(element)
        logger.info(f"Element {element} checked")


async def element_checkbox_handler(
    event: CallbackQuery,
    checkbox: ManagedCheckbox,
    manager: DialogManager,
):
    data = manager.dialog_data
    pos = int(checkbox.widget.widget_id.split("_")[-1])
    element = data["elements"][pos]
    if checkbox.is_checked():
        data["checked_elements"].remove(element)
        logger.info(f"Element {element} unchecked")
    else:
        data["checked_elements"].append(element)
        logger.info(f"Element {element} checked")


async def distribution_elements_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    gateway = get_barsic_web_gateway()
    report_map = {
        "finance_report": ReportType.GoogleReport,
        "total_by_day": ReportType.PlatAgentReport,
    }
    report_type = report_map[manager.dialog_data["report_type"]]
    response = await gateway.get_services_groups(report_type=report_type)
    services_groups = [ServicesGroup.model_validate(raw) for raw in response.json()]
    await manager.update(
        {
            "services_groups": services_groups,
        }
    )
    await manager.switch_to(ServiceDistributionMenu.ADD_ELEMENTS)


async def add_elements_radio_handler(
    event: CallbackQuery,
    select: ManagedRadio,
    manager: DialogManager,
    data: Any,
):
    checked_elements = manager.dialog_data["checked_elements"]
    gateway = get_barsic_web_gateway()
    services_group = None
    for group in manager.dialog_data["services_groups"]:
        if str(group.id) == str(data):
            services_group = group

    await gateway.add_service_element(services_group.id, checked_elements)
    logger.info(f"Service elements '{checked_elements}' added to group '{services_group}'")

    added_elements = "\n".join([f"💎 {el}" for el in checked_elements])
    await manager.update(
        {
            "result_text": f"В группу '{services_group.title}' добавлены:\n{added_elements}",
        }
    )
    manager.dialog_data["checked_elements"] = []
    await manager.switch_to(ServiceDistributionMenu.END)


async def delete_elements_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    data = manager.dialog_data
    checked_elements = data["checked_elements"]
    gateway = get_barsic_web_gateway()

    for el in checked_elements:
        await gateway.delete_service_element(el.id)
        logger.warning(f"Service element '{el.title}' deleted from group '{manager.dialog_data['services_group']}'")

    deleted_elements = "\n".join([f"💥 {el.title}" for el in checked_elements])
    await manager.update(
        {
            "result_text": f"Из группы '{manager.dialog_data['services_group']}' удалены:\n{deleted_elements}",
        }
    )
    data["checked_elements"] = []
    await manager.switch_to(ServiceDistributionMenu.END)


async def report_menu_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
    }


async def services_groups_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    services_groups = [(group.title, group.id) for group in dialog_manager.dialog_data["services_groups"]]
    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "services_groups": services_groups,
    }


async def service_elements_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    elements = [(el.title, el.id) for el in dialog_manager.dialog_data["elements"]]
    while len(elements) < settings.checkbox_size:
        elements.append(("", ""))

    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "services_group": dialog_manager.dialog_data["services_group"],
        "elements": elements,
    }


async def distribution_elements_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    new_elements = deepcopy(dialog_manager.dialog_data["new_elements"])
    while len(new_elements) < settings.checkbox_size:
        new_elements.append("")

    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "new_elements": new_elements,
    }


async def add_elements_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "services_groups": [(group.title, group.id) for group in dialog_manager.dialog_data["services_groups"]],
        "new_elements": dialog_manager.dialog_data["new_elements"],
    }


async def delete_services_element_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "services_group": dialog_manager.dialog_data["services_group"],
        "service_element": dialog_manager.dialog_data["service_element"],
    }


def is_element_not_null(data: dict, widget: Checkbox, manager: DialogManager) -> bool:
    pos = int(widget.widget_id.split("_")[-1])
    return pos < len(manager.dialog_data["elements"])


def is_new_element_not_null(data: dict, widget: Checkbox, manager: DialogManager) -> bool:
    pos = int(widget.widget_id.split("_")[-1])
    return pos < len(manager.dialog_data["new_elements"])


service_distribution_menu = Dialog(
    Window(
        Const("Распределение услуг"),
        Button(
            Const("Финансовый отчет"),
            id="finance_report",
            on_click=start_btn_handler,
        ),
        Button(
            Const("Отчет платежного агента"),
            id="total_by_day",
            on_click=start_btn_handler,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        state=ServiceDistributionMenu.START,
    ),
    Window(
        Format("{report_name}"),
        Button(
            Const("Поиск новых услуг"),
            id="search_new_services",
            on_click=search_new_services_btn_handler,
        ),
        Button(
            Const("Группы услуг"),
            id="view_services_groups",
            on_click=view_services_groups_btn_handler,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=report_menu_getter,
        state=ServiceDistributionMenu.REPORT_MENU,
    ),
    Window(
        Format("{report_name}"),
        Format("Нераспределенные элементы:"),
        Column(
            *[
                Checkbox(
                    checked_text=Format(f"🌱 {{new_elements[{pos}]}}"),
                    unchecked_text=Format(f"⛌ {{new_elements[{pos}]}}"),
                    id=f"new_element_{pos}",
                    on_click=new_element_checkbox_handler,
                    when=is_new_element_not_null,
                )
                for pos in range(settings.checkbox_size)
            ],
        ),
        # Row(
        #     Button(
        #         Const("⏮"),
        #         id="all_left",
        #         on_click=first_page_handler,
        #     ),
        #     Button(
        #         Const("◀"),
        #         id="left",
        #         on_click=back_page_handler,
        #     ),
        #     Button(
        #         Const("▶"),
        #         id="right",
        #         on_click=next_page_handler,
        #     ),
        #     Button(
        #         Const("⏭"),
        #         id="all_right",
        #         on_click=last_page_handler,
        #     ),
        # ),
        Button(
            Const("🚚 Распределить выбранные в..."),
            id="distribution_elements",
            on_click=distribution_elements_btn_handler,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=distribution_elements_getter,
        state=ServiceDistributionMenu.DISTRIBUTION_ELEMENTS,
    ),
    Window(
        Format("{report_name}"),
        Format("Распределить выбранные в..."),
        Column(
            Radio(
                checked_text=Format("{item[0]}"),
                unchecked_text=Format("{item[0]}"),
                id="r_services_groups",
                item_id_getter=operator.itemgetter(1),
                items="services_groups",
                on_click=add_elements_radio_handler,
            ),
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=add_elements_getter,
        state=ServiceDistributionMenu.ADD_ELEMENTS,
    ),
    Window(
        Format("{report_name}"),
        Format("Группы услуг"),
        Column(
            Radio(
                checked_text=Format("{item[0]}"),
                unchecked_text=Format("{item[0]}"),
                id="r_services_groups",
                item_id_getter=operator.itemgetter(1),
                items="services_groups",
                on_click=services_groups_radio_handler,
            ),
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=services_groups_getter,
        state=ServiceDistributionMenu.SERVICES_GROUPS,
    ),
    Window(
        Format("{report_name}"),
        Format("Группа: '{services_group}'"),
        Column(
            *[
                Checkbox(
                    checked_text=Format(f"🌱 {{elements[{pos}][0]}}"),
                    unchecked_text=Format(f"⛌ {{elements[{pos}][0]}}"),
                    id=f"element_{pos}",
                    on_click=element_checkbox_handler,
                    when=is_element_not_null,
                )
                for pos in range(settings.checkbox_size)
            ],
        ),
        # Row(
        #     Button(
        #         Const("⏮"),
        #         id="all_left",
        #         on_click=first_page_handler,
        #     ),
        #     Button(
        #         Const("◀"),
        #         id="left",
        #         on_click=back_page_handler,
        #     ),
        #     Button(
        #         Const("▶"),
        #         id="right",
        #         on_click=next_page_handler,
        #     ),
        #     Button(
        #         Const("⏭"),
        #         id="all_right",
        #         on_click=last_page_handler,
        #     ),
        # ),
        Button(
            Const("🗑️ Удалить выбранные"),
            id="delete_elements",
            on_click=delete_elements_btn_handler,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=service_elements_getter,
        state=ServiceDistributionMenu.SERVICES_GROUP_ELEMENTS,
    ),
    Window(
        Format("{dialog_data[result_text]}"),
        state=ServiceDistributionMenu.END,
    ),
    on_start=on_dialog_start,
)
