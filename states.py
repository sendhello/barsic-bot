from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    AUTHORIZATION = State()
    START = State()


class ReportMenu(StatesGroup):
    START = State()
    CHOOSE_REPORT = State()
    CHANGE_START_DATE = State()
    CHANGE_END_DATE = State()
    BUILD_REPORT = State()
    SHOW_REPORT = State()


class ServiceDistributionMenu(StatesGroup):
    START = State()
    FOUND_SERVICES = State()
