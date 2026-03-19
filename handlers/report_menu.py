import logging
from datetime import date
from math import ceil
from typing import Any

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
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from constants import ADMIN_KEY, PERMISSION_ID, REPORT_NAME_MAP, ButtonID, button_text
from core.settings import settings
from gateways.client import get_barsic_web_gateway
from repositories.redis_repo import get_redis_repo
from schemas.report import (
    AttendanceReportResult,
    CorpServicesSumReportResult,
    FinanceReportResult,
    PeopleInZone,
    TotalByDayResult,
)
from states import ReportMenu

logger = logging.getLogger(__name__)
MIN_PAGE_SIZE = 1


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
    manager.dialog_data["goods"] = list(settings.purchased_goods_report_positions)
    manager.dialog_data["checked_goods"] = []
    manager.dialog_data["goods_page"] = 0


def _get_page_size() -> int:
    return max(settings.checkbox_size, MIN_PAGE_SIZE)


def _get_goods_page_data(dialog_manager: DialogManager) -> tuple[int, int]:
    goods_count = len(dialog_manager.dialog_data.get("goods", []))
    total_pages = max(1, ceil(goods_count / _get_page_size())) if goods_count else 1
    current_page = dialog_manager.dialog_data.get("goods_page", 0)
    current_page = max(0, min(current_page, total_pages - 1))
    return current_page, total_pages


async def _sync_goods_checkboxes(manager: DialogManager):
    current_page, _ = _get_goods_page_data(manager)
    page_size = _get_page_size()
    checked_goods = manager.dialog_data.get("checked_goods", [])
    goods = manager.dialog_data.get("goods", [])

    for pos in range(settings.checkbox_size):
        good_position = current_page * page_size + pos
        is_checked = False
        if good_position < len(goods):
            is_checked = goods[good_position] in checked_goods

        await manager.find(f"good_{pos}").set_checked(is_checked)


async def choose_goods_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    current_page, total_pages = _get_goods_page_data(dialog_manager)
    goods = list(dialog_manager.dialog_data["goods"])
    page_size = _get_page_size()
    goods = goods[current_page * page_size : (current_page + 1) * page_size]
    while len(goods) < settings.checkbox_size:
        goods.append("")

    return {
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
        "goods": goods,
        "goods_page": current_page,
        "goods_page_human": current_page + 1,
        "goods_total_pages": total_pages,
    }


def is_goods_not_null(data: dict, widget: Checkbox, manager: DialogManager) -> bool:
    pos = int(widget.widget_id.split("_")[-1])
    current_page, _ = _get_goods_page_data(manager)
    good_position = current_page * _get_page_size() + pos
    return good_position < len(manager.dialog_data["goods"])


def has_goods_prev_page(data: dict, widget: Button, manager: DialogManager) -> bool:
    return data["goods_page"] > 0


def has_goods_next_page(data: dict, widget: Button, manager: DialogManager) -> bool:
    return data["goods_page"] < data["goods_total_pages"] - 1


async def goods_checkbox_handler(
    event: CallbackQuery,
    checkbox: ManagedCheckbox,
    manager: DialogManager,
):
    data = manager.dialog_data
    checked_goods = data["checked_goods"]
    pos = int(checkbox.widget.widget_id.split("_")[-1])
    current_page, _ = _get_goods_page_data(manager)
    good_position = current_page * _get_page_size() + pos
    if good_position >= len(data["goods"]):
        return
    good = data["goods"][good_position]
    if checkbox.is_checked():
        if good in checked_goods:
            checked_goods.remove(good)
        logger.info(f"Element {good} unchecked")
    else:
        if good not in checked_goods:
            checked_goods.append(good)
        logger.info(f"Element {good} checked")


async def goods_prev_page_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    current_page, _ = _get_goods_page_data(manager)
    if current_page <= 0:
        return
    await manager.update({"goods_page": current_page - 1})
    await _sync_goods_checkboxes(manager)


async def goods_first_page_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    current_page, _ = _get_goods_page_data(manager)
    if current_page <= 0:
        return
    await manager.update({"goods_page": 0})
    await _sync_goods_checkboxes(manager)


async def goods_next_page_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    current_page, total_pages = _get_goods_page_data(manager)
    if current_page >= total_pages - 1:
        return
    await manager.update({"goods_page": current_page + 1})
    await _sync_goods_checkboxes(manager)


async def goods_last_page_btn_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    current_page, total_pages = _get_goods_page_data(manager)
    if current_page >= total_pages - 1:
        return
    await manager.update({"goods_page": total_pages - 1})
    await _sync_goods_checkboxes(manager)


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


async def finance_report_checkboxes_getter(dialog_manager: DialogManager, **kwargs) -> dict[str, Any]:
    hide_zero_text = "Скрывать нули" if dialog_manager.find("hide_zero").is_checked() else "Не скрывать нули"

    if dialog_manager.find("use_yadisk").is_checked():
        use_yadisk_text = "Сохранять отчеты в YandexDisk"
    else:
        use_yadisk_text = "Не сохранять отчеты в YandexDisk"

    if dialog_manager.find("telegram_report").is_checked():
        telegram_report_text = "Отправлять сообщение в Telegram"
    else:
        telegram_report_text = "Не отправлять сообщение в Telegram"

    use_cache_text = "Использовать кеш" if dialog_manager.find("use_cache").is_checked() else "Не использовать кеш"

    if dialog_manager.find("use_google").is_checked():
        use_google_text = "Сохранять отчеты в Google"
    else:
        use_google_text = "Не сохранять отчеты в Google"

    return {
        "hide_zero_text": hide_zero_text,
        "use_yadisk_text": use_yadisk_text,
        "telegram_report_text": telegram_report_text,
        "use_cache_text": use_cache_text,
        "use_google_text": use_google_text,
        "report_name": REPORT_NAME_MAP[dialog_manager.dialog_data["report_type"]],
    }


async def get_client_count() -> PeopleInZone:
    gateway = get_barsic_web_gateway()
    response = await gateway.post(url="/api/v1/reports/client_count")
    return PeopleInZone.model_validate(response.json())


def is_only_admin(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["user_permission"] == ADMIN_KEY


def is_finance_report(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "finance_report"


def is_total_by_day(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "total_by_day"


def is_purchased_goods_report(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "purchased_goods_report"


def is_attendance_report(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] == "attendance_report"


def is_not_purchased_goods_report(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] != "purchased_goods_report"


def is_total_by_day_or_attendance_report(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    return data["dialog_data"]["report_type"] in ["total_by_day", "attendance_report"]


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


async def run_attendance_report(
    start_date: date,
    end_date: date | None,
    save_to_yandex: bool,
    save_to_google: bool,
    use_cache: bool,
) -> AttendanceReportResult:
    if end_date is None:
        end_date = start_date

    gateway = get_barsic_web_gateway()
    response = await gateway.create_attendance_report(
        start_date=start_date,
        end_date=end_date,
        save_to_yandex=save_to_yandex,
        save_to_google=save_to_google,
        use_cache=use_cache,
    )
    return AttendanceReportResult.model_validate(response.json())


def get_attendance_report_details(
    result: AttendanceReportResult,
    save_to_google: bool,
    save_to_yandex: bool,
) -> str:
    details = []
    if save_to_google and result.google_report is not None:
        details.append(f"Google: {result.google_report}")
    if save_to_yandex and result.yandex_public_url is not None:
        details.append(f"Yandex: {result.yandex_public_url}")
    if save_to_yandex and result.yandex_download_link is not None:
        details.append(f"Yandex (скачать): {result.yandex_download_link}")
    if not details and result.local_path is not None:
        details.append(f"Локальный файл: {result.local_path}")

    return "\n".join(details)


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
    use_google = manager.find("use_google").is_checked()

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

        case "attendance_report":
            result = await run_attendance_report(
                start_date=start_date,
                end_date=end_date,
                save_to_yandex=use_yadisk,
                save_to_google=use_google,
                use_cache=use_cache,
            )
            message = f"{'Отчет по количеству в разрезе дня сформирован' if result.ok else 'Ошибка'}"
            detail = get_attendance_report_details(result, use_google, use_yadisk) if result.ok else result.detail
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
    await manager.update({"goods_page": 0})
    await manager.switch_to(ReportMenu.CHOOSE_GOODS)
    await _sync_goods_checkboxes(manager)


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
        Button(
            Const("Отчет по количеству в разрезе дня"),
            id="attendance_report",
            on_click=choose_report,
            when=is_only_admin,
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
            checked_text=Const("[x] Сохранять в YandexDisk"),
            unchecked_text=Const("[ ] Не сохранять в YandexDisk"),
            id="use_yadisk",
            default=False,
            when=is_attendance_report,
        ),
        Checkbox(
            checked_text=Const("[x] Сохранять в Google"),
            unchecked_text=Const("[ ] Не сохранять в Google"),
            id="use_google",
            default=True,
            when=is_attendance_report,
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
            when=is_total_by_day_or_attendance_report,
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
                for pos in range(settings.checkbox_size)
            ],
        ),
        Format("Страница {goods_page_human}/{goods_total_pages}"),
        Row(
            Button(
                Const("⏮"),
                id="goods_first_page",
                on_click=goods_first_page_btn_handler,
                when=has_goods_prev_page,
            ),
            Button(
                Const("◀"),
                id="goods_prev_page",
                on_click=goods_prev_page_btn_handler,
                when=has_goods_prev_page,
            ),
            Button(
                Const("▶"),
                id="goods_next_page",
                on_click=goods_next_page_btn_handler,
                when=has_goods_next_page,
            ),
            Button(
                Const("⏭"),
                id="goods_last_page",
                on_click=goods_last_page_btn_handler,
                when=has_goods_next_page,
            ),
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
