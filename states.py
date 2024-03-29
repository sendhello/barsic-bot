from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    START = State()
    reports_menu_state = State()
    choose_period_state = State()
    choose_date_from_state = State()
    choose_date_to_state = State()
    set_period_state = State()
    request_state = State()
    print_state = State()
    save_state = State()


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
