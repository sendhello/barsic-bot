from enum import StrEnum, auto

USER_KEY = "user"
ADMIN_KEY = "admin"
PERMISSION_ID = "bot_permission"
LIMIT_ID = "password_limit"
BLOCKED_USER_ID = "user_blocked"


class ButtonID(StrEnum):
    START = auto()
    HELP = auto()
    REPORTS = auto()
    SET_COMMANDS = auto()

    TODAY = auto()
    YESTERDAY = auto()
    OTHER_PERIOD = auto()
    SET = auto()
    REQUEST = auto()
    CANCEL = "__cancel__"
    PRINT = auto()
    SAVE = auto()
    CHANGE_PERIOD = auto()
    HOME = auto()


def button_text(id_: ButtonID) -> str:
    text = {
        ButtonID.START: "🏁 Старт",
        ButtonID.HELP: "ℹ️ Помощь",
        ButtonID.CANCEL: "❌ Отмена",
    }
    return text.get(id_)


class ReportType(StrEnum):
    GoogleReport = "GoogleReport"
    PlatAgentReport = "PlatAgentReport"
    ItogReport = "ItogReport"
    Attendance = "attendance"


REPORT_NAME_MAP = {
    "finance_report": "Финансовый отчет",
    "total_by_day": "Итоговый отчет с разбивкой",
    "purchased_goods_report": "Отчет по купленным товарам",
    "attendance_report": "Отчет по количеству в разрезе дня",
}
