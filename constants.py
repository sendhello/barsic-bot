from enum import StrEnum, auto


USER_KEY = "user"
ADMIN_KEY = "admin"
PERMISSION_ID = "bot_permission"
LIMIT_ID = "password_limit"
BLOCKED_USER_ID = "user_blocked"


class ReportType(StrEnum):
    PEOPLE_IN_ZONE = auto()
    TOTAL_REPORT = auto()
    CASH_REPORT = auto()


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
    CANCEL = auto()
    PRINT = auto()
    SAVE = auto()
    CHANGE_PERIOD = auto()
    HOME = auto()


def text(id_: ReportType | ButtonID) -> str:
    button_text = {
        ButtonID.START: "Старт",
        ButtonID.HELP: "Помощь",
        ButtonID.REPORTS: "Отчеты",
        ButtonID.SET_COMMANDS: "Обновить команды",
        ReportType.PEOPLE_IN_ZONE: "Люди в зоне",
        ReportType.TOTAL_REPORT: "Финансовый отчет",
        ReportType.CASH_REPORT: "Суммовой отчет",
        ButtonID.TODAY: "За сегодня",
        ButtonID.YESTERDAY: "За вчера",
        ButtonID.OTHER_PERIOD: "Произвольный период",
        ButtonID.SET: "Установить",
        ButtonID.REQUEST: "Выполнить запрос",
        ButtonID.CANCEL: "Отменить",
        ButtonID.PRINT: "Напечатать на экране",
        ButtonID.SAVE: "Сохранить",
        ButtonID.CHANGE_PERIOD: "Изменить период",
        ButtonID.HOME: "На главную",
    }
    return button_text.get(id_)
