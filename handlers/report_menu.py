import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Button, Calendar, Cancel, Checkbox, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from gateways.client import get_barsic_web_gateway
from schemas.report import FinanceReportResult, PeopleInZone, TotalByDayResult
from states import ReportMenu


logger = logging.getLogger(__name__)

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }
    manager.dialog_data["project"] = project
    manager.dialog_data["start_date"] = date.today()
    manager.dialog_data["end_date"] = date.today()


async def choose_report(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await callback.answer()
    await manager.update({"report_type": button.widget_id})
    await manager.switch_to(ReportMenu.CHOOSE_REPORT)


async def on_start_date_selected(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    await callback.answer()
    manager.dialog_data["start_date"] = selected_date
    await manager.switch_to(ReportMenu.CHOOSE_REPORT)


async def on_end_date_selected(callback: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    await callback.answer()
    manager.dialog_data["end_date"] = selected_date
    await manager.switch_to(ReportMenu.CHOOSE_REPORT)


async def finance_report_checkboxes_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    if dialog_manager.find("use_yadisk").is_checked():
        use_yadisk_text = "Сохранять отчеты в YandexDisk"
    else:
        use_yadisk_text = "Не сохранять отчеты в YandexDisk"

    if dialog_manager.find("telegram_report").is_checked():
        telegram_report_text = "Отправлять сообщение в Telegram"
    else:
        telegram_report_text = "Не отправлять сообщение в Telegram"

    return {
        "use_yadisk_text": use_yadisk_text,
        "telegram_report_text": telegram_report_text,
    }


async def get_client_count() -> PeopleInZone:
    gateway = get_barsic_web_gateway()
    response = await gateway.post(url="/api/v1/reports/client_count")
    return PeopleInZone.model_validate(response.json())


def is_not_people_in_zone(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] != "people_in_zone"


def is_finance_report(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "finance_report"


async def run_finance_report(
    start_date: date, end_date: date | None, use_yadisk: bool, telegram_report: bool
) -> FinanceReportResult:
    if end_date is None:
        end_date = start_date

    gateway = get_barsic_web_gateway()
    response = await gateway.post(
        url="/api/v1/reports/create_reports",
        params={
            "date_from": datetime.combine(start_date, datetime.min.time()),
            "date_to": datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
            "use_yadisk": use_yadisk,
            "telegram_report": telegram_report,
        },
    )
    return FinanceReportResult.model_validate(response.json())


async def run_total_by_day(start_date: date, end_date: date | None) -> TotalByDayResult:
    start_date = date(end_date.year, end_date.month, 1)

    gateway = get_barsic_web_gateway()
    response = await gateway.post(
        url="/api/v1/reports/create_total_report_by_day",
        params={
            "date_from": datetime.combine(start_date, datetime.min.time()),
            "date_to": datetime.combine(end_date + timedelta(days=1), datetime.min.time()),
            "db_name": "Aquapark_Ulyanovsk",
        },
    )
    return TotalByDayResult.model_validate(response.json())


async def run_report(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    report_type = manager.dialog_data["report_type"]
    start_date = manager.dialog_data["start_date"]
    end_date = manager.dialog_data["end_date"]
    use_yadisk = manager.find("use_yadisk").is_checked()
    telegram_report = manager.find("telegram_report").is_checked()

    match report_type:

        case "people_in_zone":
            people_in_zone_report = await get_client_count()
            await manager.update(
                {
                    "report_result": (
                        "Количество людей в зоне\n"
                        f"Аквазона: {people_in_zone_report.aquazone}\n"
                        f"Всего: {people_in_zone_report.total}"
                    ),
                }
            )
            await manager.switch_to(ReportMenu.SHOW_REPORT)

        case "finance_report":
            result = await run_finance_report(
                start_date=start_date,
                end_date=end_date,
                use_yadisk=use_yadisk,
                telegram_report=telegram_report,
            )
            message = f"{'Финансовый отчет сформирован' if result.ok else 'При формировании итогового отчета произошла ошибка'}"
            detail = f"{result.google_report}"
            await manager.update({"report_result": f"{message}\n{detail}"})
            await manager.switch_to(ReportMenu.SHOW_REPORT)

        case "total_by_day":
            result = await run_total_by_day(
                start_date=start_date,
                end_date=end_date,
            )
            message = f"{'Итоговый отчет с разбивкой сформирован' if result.ok else 'При формировании итогового отчета произошла ошибка'}"
            detail = f"{result.google_report}"
            await manager.update({"report_result": f"{message}\n{detail}"})
            await manager.switch_to(ReportMenu.SHOW_REPORT)

        case _:
            logger.error(f"Неверный тип отчета: {report_type}")
            await manager.switch_to(ReportMenu.CHOOSE_REPORT)


report_menu = Dialog(
    Window(
        Const("Отчеты"),
        Format("Выберите тип отчета"),
        Button(
            Const("Люди в зоне"),
            id="people_in_zone",
            on_click=choose_report,
        ),
        Button(
            Const("Финансовый отчет"),
            id="finance_report",
            on_click=choose_report,
        ),
        Button(
            Const("Итоговый с разбивкой"),
            id="total_by_day",
            on_click=choose_report,
        ),
        Cancel(text=Const("Отмена")),
        state=ReportMenu.START,
    ),
    Window(
        Const("Отчеты"),
        Format("Тип отчета: {dialog_data[report_type]}"),
        Format("Период: с {dialog_data[start_date]} по {dialog_data[end_date]}", when=is_not_people_in_zone),
        Format("{use_yadisk_text}", when=is_finance_report),
        Format("{telegram_report_text}", when=is_finance_report),
        SwitchTo(
            Const("Изменить дату начала периода"),
            id="change_start_date",
            state=ReportMenu.CHANGE_START_DATE,
            when=is_not_people_in_zone,
        ),
        SwitchTo(
            Const("Изменить дату конца периода"),
            id="change_end_date",
            state=ReportMenu.CHANGE_END_DATE,
            when=is_not_people_in_zone,
        ),
        Checkbox(
            checked_text=Const("[x] Сохранять в YandexDisk"),
            unchecked_text=Const("[ ] Не сохранять в YandexDisk"),
            id="use_yadisk",
            when=is_finance_report,
        ),
        Checkbox(
            checked_text=Const("[x] Отправлять в Telegram"),
            unchecked_text=Const("[ ] Не отправлять в Telegram"),
            id="telegram_report",
            when=is_finance_report,
        ),
        Button(
            Const("Сформировать отчет"),
            id="build_report",
            on_click=run_report,
        ),
        Cancel(text=Const("Отмена")),
        getter=finance_report_checkboxes_getter,
        state=ReportMenu.CHOOSE_REPORT,
    ),
    Window(
        Const("Изменить дату начала периода"),
        Calendar(id="calendar", on_click=on_start_date_selected),
        Cancel(text=Const("Отмена")),
        state=ReportMenu.CHANGE_START_DATE,
    ),
    Window(
        Const("Изменить дату конца периода"),
        Calendar(id="calendar", on_click=on_end_date_selected),
        Cancel(text=Const("Отмена")),
        state=ReportMenu.CHANGE_END_DATE,
    ),
    Window(
        Format("{dialog_data[report_result]}"),
        state=ReportMenu.SHOW_REPORT,
    ),
    on_start=on_dialog_start,
)
