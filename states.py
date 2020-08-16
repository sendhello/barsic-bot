from aiogram.dispatcher.filters.state import State, StatesGroup


class GeneralMenu(StatesGroup):
    general_menu_state = State()


class ReportsStates(StatesGroup):
    reports_menu_state = State()
    choose_period_state = State()
    choose_date_from_state = State()
    choose_date_to_state = State()
    set_period_state = State()
    request_state = State()
    print_state = State()
    save_state = State()
