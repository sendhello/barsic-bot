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
        ButtonID.START: "🏁Старт",
        ButtonID.HELP: "ℹ️Помощь",
        ButtonID.CANCEL: "❌Отмена",
    }
    return text.get(id_)
