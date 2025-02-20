from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    AUTHORIZATION = State()
    START = State()


class ReportMenu(StatesGroup):
    START = State()
    CHOOSE_REPORT = State()
    CHANGE_START_DATE = State()
    CHANGE_END_DATE = State()
    CHOOSE_GOODS = State()
    BUILD_REPORT = State()
    SHOW_REPORT = State()


class InfoMenu(StatesGroup):
    START = State()
    CHOOSE_INFO = State()
    CHANGE_START_DATE = State()
    CHANGE_END_DATE = State()
    SHOW_STATE = State()


class ServiceDistributionMenu(StatesGroup):
    START = State()
    REPORT_MENU = State()
    SERVICES_GROUPS = State()
    SERVICES_GROUP_ELEMENTS = State()
    DELETE_SERVICES_ELEMENT = State()
    ADD_ELEMENTS = State()
    DISTRIBUTION_ELEMENTS = State()
    END = State()


# for pos in range(100):
#     state_name = f"DISTRIBUTION_ELEMENTS_{pos}"
#     state = State(state=state_name, group_name='ServiceDistributionMenu')
#     state._group = ServiceDistributionMenu
#     setattr(
#         ServiceDistributionMenu,
#         state_name,
#         state
#     )
