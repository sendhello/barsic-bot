import logging
from datetime import date
from typing import Any, Dict

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import (
    Button,
    Calendar,
    CalendarConfig,
    Cancel,
    Checkbox,
    Column,
    ManagedCheckbox,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from constants import ADMIN_KEY, PERMISSION_ID, REPORT_NAME_MAP, ButtonID, button_text
from core.settings import settings
from gateways.client import get_barsic_web_gateway
from repositories.redis_repo import get_redis_repo
from schemas.report import CorpServicesSumReportResult, FinanceReportResult, PeopleInZone, TotalByDayResult
from states import ReportMenu


logger = logging.getLogger(__name__)


async def on_dialog_start(start_data: Any, manager: DialogManager):
    project = {
        "name": "Barsic Bot",
    }

    user_id = manager.event.from_user.id
    redis_repo = await get_redis_repo()
    permission = await redis_repo.get_from_cache(key=f"{PERMISSION_ID}:{user_id}")
    manager.dialog_data["user_permission"] = permission

    manager.dialog_data["project"] = project
    manager.dialog_data["start_date"] = date.today()
    manager.dialog_data["end_date"] = date.today()
    manager.dialog_data["goods"] = settings.purchased_goods_report_positions
    manager.dialog_data["checked_goods"] = []


async def choose_goods_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    goods = dialog_manager.dialog_data["goods"]
    while len(goods) < settings.checkbox_size:
        goods.append(("", ""))

    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "goods": goods,
    }


def is_goods_not_null(data: dict, widget: Checkbox, manager: DialogManager) -> bool:
    pos = int(widget.widget_id.split("_")[-1])
    return pos < len(manager.dialog_data["goods"])


async def goods_checkbox_handler(
    event: CallbackQuery,
    checkbox: ManagedCheckbox,
    manager: DialogManager,
):
    data = manager.dialog_data
    pos = int(checkbox.widget.widget_id.split("_")[-1])
    good = data["goods"][pos]
    if checkbox.is_checked():
        data["checked_goods"].remove(good)
        logger.info(f"Element {good} unchecked")
    else:
        data["checked_goods"].append(good)
        logger.info(f"Element {good} checked")


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
    if dialog_manager.find("hide_zero").is_checked():
        hide_zero_text = "Скрывать нули"
    else:
        hide_zero_text = "Не скрывать нули"

    if dialog_manager.find("use_yadisk").is_checked():
        use_yadisk_text = "Сохранять отчеты в YandexDisk"
    else:
        use_yadisk_text = "Не сохранять отчеты в YandexDisk"

    if dialog_manager.find("telegram_report").is_checked():
        telegram_report_text = "Отправлять сообщение в Telegram"
    else:
        telegram_report_text = "Не отправлять сообщение в Telegram"

    if dialog_manager.find("use_cache").is_checked():
        use_cache_text = "Использовать кеш"
    else:
        use_cache_text = "Не использовать кеш"

    report_name_map = {
        "finance_report": "Финансовый отчет",
        "total_by_day": "Итоговый отчет с разбивкой",
        "purchased_goods_report": "Отчет по купленным товарам",
    }

    return {
        "hide_zero_text": hide_zero_text,
        "use_yadisk_text": use_yadisk_text,
        "telegram_report_text": telegram_report_text,
        "use_cache_text": use_cache_text,
        "report_name": report_name_map[dialog_manager.dialog_data["report_type"]],
    }


async def get_client_count() -> PeopleInZone:
    gateway = get_barsic_web_gateway()
    response = await gateway.post(url="/api/v1/reports/client_count")
    return PeopleInZone.model_validate(response.json())


def is_only_admin(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["user_permission"] == ADMIN_KEY


def is_finance_report(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "finance_report"


def is_total_by_day(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "total_by_day"


def is_purchased_goods_report(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "purchased_goods_report"


def is_not_purchased_goods_report(data: Dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] != "purchased_goods_report"


async def run_finance_report(
    start_date: date, end_date: date | None, use_yadisk: bool, telegram_report: bool
) -> FinanceReportResult:
    if end_date is None:
        end_date = start_date

    gateway = get_barsic_web_gateway()
    response = await gateway.create_reports(
        start_date=start_date,
        end_date=end_date,
        use_yadisk=use_yadisk,
        telegram_report=telegram_report,
    )
    return FinanceReportResult.model_validate(response.json())


async def run_total_by_day(start_date: date, end_date: date | None, use_cache: bool = True) -> TotalByDayResult:
    start_date = date(end_date.year, end_date.month, 1)

    gateway = get_barsic_web_gateway()
    response = await gateway.create_total_report_by_day(
        start_date=start_date,
        end_date=end_date,
        use_cache=use_cache,
        db_name="Aquapark_Ulyanovsk",
    )
    return TotalByDayResult.model_validate(response.json())


async def run_purchased_goods_report(
    start_date: date, end_date: date | None, goods: list[str], use_yadisk: bool = True, hide_zero: bool = True
) -> CorpServicesSumReportResult:
    if end_date is None:
        end_date = start_date

    gateway = get_barsic_web_gateway()
    response = await gateway.create_purchased_goods_report(
        start_date=start_date,
        end_date=end_date,
        goods=goods,
        use_yadisk=use_yadisk,
        hide_zero=hide_zero,
        db_name="Aquapark_Ulyanovsk",
    )
    return CorpServicesSumReportResult.model_validate(response.json())


async def run_report(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    report_type = manager.dialog_data["report_type"]
    start_date = manager.dialog_data["start_date"]
    end_date = manager.dialog_data["end_date"]
    checked_goods = manager.dialog_data["checked_goods"]
    use_yadisk = manager.find("use_yadisk").is_checked()
    hide_zero = manager.find("hide_zero").is_checked()
    telegram_report = manager.find("telegram_report").is_checked()
    use_cache = manager.find("use_cache").is_checked()

    match report_type:

        case "finance_report":
            result = await run_finance_report(
                start_date=start_date,
                end_date=end_date,
                use_yadisk=use_yadisk,
                telegram_report=telegram_report,
            )
            message = f"{'Финансовый отчет сформирован' if result.ok else 'Ошибка'}"
            detail = f"{result.google_report}" if result.ok else result.detail
            await manager.update({"report_result": f"{message}\n{detail}"})
            await manager.switch_to(ReportMenu.SHOW_REPORT)

        case "total_by_day":
            result = await run_total_by_day(
                start_date=start_date,
                end_date=end_date,
                use_cache=use_cache,
            )
            message = f"{'Итоговый отчет с разбивкой сформирован' if result.ok else 'Ошибка'}"
            detail = f"{result.google_report}" if result.ok else result.detail
            await manager.update({"report_result": f"{message}\n{detail}"})
            await manager.switch_to(ReportMenu.SHOW_REPORT)

        case "purchased_goods_report":
            result = await run_purchased_goods_report(
                start_date=start_date,
                end_date=end_date,
                goods=checked_goods,
                use_yadisk=use_yadisk,
                hide_zero=hide_zero,
            )
            manager.dialog_data["checked_goods"] = []
            message = f"{'Отчет по купленным товарам сформирован' if result.ok else 'Ошибка'}"
            detail = f"{result.public_url or result.local_path}" if result.ok else result.detail
            await manager.update({"report_result": f"{message}\n{detail}"})
            await manager.switch_to(ReportMenu.SHOW_REPORT)

        case _:
            logger.error(f"Неверный тип отчета: {report_type}")
            await manager.switch_to(ReportMenu.CHOOSE_REPORT)


async def choose_goods(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await manager.switch_to(ReportMenu.CHOOSE_GOODS)


report_menu = Dialog(
    Window(
        Const("Отчеты"),
        Format("Выберите тип отчета"),
        Button(
            Const("Финансовый отчет"),
            id="finance_report",
            on_click=choose_report,
            when=is_only_admin,
        ),
        Button(
            Const("Итоговый с разбивкой"),
            id="total_by_day",
            on_click=choose_report,
            when=is_only_admin,
        ),
        Button(
            Const("По купленным товарам"),
            id="purchased_goods_report",
            on_click=choose_report,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        state=ReportMenu.START,
    ),
    Window(
        Format("{report_name}"),
        SwitchTo(
            Format("Начало периода: {dialog_data[start_date]}"),
            id="change_start_date",
            state=ReportMenu.CHANGE_START_DATE,
        ),
        SwitchTo(
            Format("Конец периода: {dialog_data[end_date]}"),
            id="change_end_date",
            state=ReportMenu.CHANGE_END_DATE,
        ),
        Checkbox(
            checked_text=Const("[x] Скрывать нули"),
            unchecked_text=Const("[ ] Не скрывать нули"),
            id="hide_zero",
            default=True,
            when=is_purchased_goods_report,
        ),
        Checkbox(
            checked_text=Const("[x] Сохранять в YandexDisk"),
            unchecked_text=Const("[ ] Не сохранять в YandexDisk"),
            id="use_yadisk",
            default=True,
            when=is_finance_report,
        ),
        Checkbox(
            checked_text=Const("[x] Сохранять в YandexDisk"),
            unchecked_text=Const("[ ] Не сохранять в YandexDisk"),
            id="use_yadisk",
            default=True,
            when=is_purchased_goods_report,
        ),
        Checkbox(
            checked_text=Const("[x] Отправлять в Telegram"),
            unchecked_text=Const("[ ] Не отправлять в Telegram"),
            id="telegram_report",
            default=True,
            when=is_finance_report,
        ),
        Checkbox(
            checked_text=Const("[x] Использовать кеш"),
            unchecked_text=Const("[ ] Не использовать кеш"),
            id="use_cache",
            default=True,
            when=is_total_by_day,
        ),
        Button(
            Const("📝 Выбрать услуги"),
            id="choose_goods",
            on_click=choose_goods,
            when=is_purchased_goods_report,
        ),
        Button(
            Const("▶️Сформировать отчет"),
            id="build_report",
            on_click=run_report,
            when=is_not_purchased_goods_report,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=finance_report_checkboxes_getter,
        state=ReportMenu.CHOOSE_REPORT,
    ),
    Window(
        Const("Дата начала периода"),
        Calendar(
            id="date_from_calendar",
            on_click=on_start_date_selected,
            config=CalendarConfig(
                min_date=date(2000, 1, 1),
                max_date=date(2100, 12, 31),
                month_columns=3,
                years_per_page=9,
                years_columns=3,
            ),
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        state=ReportMenu.CHANGE_START_DATE,
    ),
    Window(
        Const("Дата конца периода"),
        Calendar(
            id="date_to_calendar",
            on_click=on_end_date_selected,
            config=CalendarConfig(
                min_date=date(2000, 1, 1),
                max_date=date(2100, 12, 31),
                month_columns=3,
                years_per_page=9,
                years_columns=3,
            ),
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        state=ReportMenu.CHANGE_END_DATE,
    ),
    Window(
        Format("{report_name}"),
        Const("Выберите услуги для отчета"),
        Column(
            *[
                Checkbox(
                    checked_text=Format(f"🌱 {{goods[{pos}]}}"),
                    unchecked_text=Format(f"⛌ {{goods[{pos}]}}"),
                    id=f"good_{pos}",
                    on_click=goods_checkbox_handler,
                    when=is_goods_not_null,
                )
                for pos in range(len(settings.purchased_goods_report_positions))
            ],
        ),
        Button(
            Const("▶️Сформировать отчет"),
            id="build_report",
            on_click=run_report,
        ),
        Cancel(text=Const(button_text(ButtonID.CANCEL))),
        getter=choose_goods_getter,
        state=ReportMenu.CHOOSE_GOODS,
    ),
    Window(
        Format("{dialog_data[report_result]}"),
        state=ReportMenu.SHOW_REPORT,
    ),
    on_start=on_dialog_start,
)
