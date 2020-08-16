from aiogram.types import ContentTypes, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from misc import dp
from .default_handler import GeneralMenu
from utils import is_correct_command
from datetime import datetime, timedelta
from callbacks import people_in_zone, total_report
from constants import Button


class ReportsStates(StatesGroup):
    menu_state = State()
    choose_period_state = State()
    choose_date_from_state = State()
    choose_date_to_state = State()
    set_period_state = State()
    request_state = State()
    print_state = State()


@dp.message_handler(state=GeneralMenu.main_menu_state, content_types=ContentTypes.TEXT)
async def reports_menu_state(message: Message, state: FSMContext):
    await ReportsStates.menu_state.set()

    if not await is_correct_command(state, message):
        return None

    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.PEOPLE_IN_ZONE, Button.TOTAL_REPORT, Button.SUM_REPORT]
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await message.answer('Выберите отчет', reply_markup=rkb)


@dp.message_handler(state=ReportsStates.menu_state, content_types=ContentTypes.TEXT)
async def choose_period_state(message: Message, state: FSMContext):
    await ReportsStates.choose_period_state.set()
    await state.update_data(report_name=message.text)

    if not await is_correct_command(state, message):
        return None

    if message.text == Button.PEOPLE_IN_ZONE:
        await set_period_state(message, state)
        return None

    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.TODAY, Button.YESTERDAY, Button.OTHER_PERIOD]
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await message.answer('Выберите период', reply_markup=rkb)


@dp.message_handler(state=ReportsStates.choose_period_state, content_types=ContentTypes.TEXT)
async def choose_date_from_state(message: Message, state: FSMContext):
    await ReportsStates.choose_date_from_state.set()

    if not await is_correct_command(state, message):
        return None

    if message.text != Button.OTHER_PERIOD:
        await set_period_state(message, state)
        return None

    date_from = datetime.now() - timedelta(100)

    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.SET]
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await state.update_data(date_from=date_from.strftime('%Y%m%d'))
    await message.answer(f'Выберите дату начала периода отчета', reply_markup=rkb)


@dp.message_handler(state=ReportsStates.choose_date_from_state, content_types=ContentTypes.TEXT)
async def choose_date_to_state(message: Message, state: FSMContext):
    await ReportsStates.choose_date_to_state.set()

    if not await is_correct_command(state, message):
        return None

    if message.text != Button.SET:
        return None

    date_to = datetime.now() - timedelta(50)

    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.SET]
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await state.update_data(date_to=date_to.strftime('%Y%m%d'))
    await message.answer(f'Выберите дату окончания периода отчета', reply_markup=rkb)


@dp.message_handler(state=ReportsStates.choose_date_to_state, content_types=ContentTypes.TEXT)
async def set_period_state(message: Message, state: FSMContext):
    await ReportsStates.set_period_state.set()

    if not await is_correct_command(state, message):
        return None

    data = await state.get_data()
    report_name = data['report_name']
    date_from = None
    date_to = None

    if message.text == Button.TODAY:
        date_from = date_to = datetime.now()
        await state.update_data(date_from=date_from.strftime('%Y%m%d'))
        await state.update_data(date_to=date_to.strftime('%Y%m%d'))
    elif message.text == Button.YESTERDAY:
        date_from = date_to = datetime.now() - timedelta(1)
        await state.update_data(date_from=date_from.strftime('%Y%m%d'))
        await state.update_data(date_to=date_to.strftime('%Y%m%d'))
    elif message.text == Button.SET:
        date_from = datetime.strptime(data.get('date_from'), '%Y%m%d')
        date_to = datetime.strptime(data.get('date_to'), '%Y%m%d')

    buttons = [Button.REQUEST, Button.CANCEL]
    message_text = f'Будет сформирован отчет {report_name}'

    if report_name != Button.PEOPLE_IN_ZONE:
        message_text += f" за {date_from.strftime('%d-%m-%Y')}" if date_from == date_to \
            else f' за период с {date_from.strftime("%d-%m-%Y")} по {date_to.strftime("%d-%m-%Y")}'
        buttons.append('Изменить период')

    rkb = ReplyKeyboardMarkup(row_width=1)
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await message.answer(message_text, reply_markup=rkb)


@dp.message_handler(state=ReportsStates.set_period_state, content_types=ContentTypes.TEXT)
async def request_state(message: Message, state: FSMContext):
    await ReportsStates.request_state.set()

    if not await is_correct_command(state, message):
        return None

    data = await state.get_data()
    report_name = data['report_name']
    result = None

    if report_name == Button.PEOPLE_IN_ZONE:
        result = await people_in_zone()
    elif report_name == Button.TOTAL_REPORT:
        result = await total_report(
            date_from=datetime.strptime(data.get('date_from'), '%Y%m%d'),
            date_to=datetime.strptime(data.get('date_to'), '%Y%m%d'))
    elif report_name == Button.SUM_REPORT:
        await message.answer(f'Пока не работает')

    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.PRINT, Button.SAVE]
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await state.update_data(result=result)
    await message.answer(f'Отчет получен', reply_markup=rkb)


@dp.message_handler(state=ReportsStates.request_state, content_types=ContentTypes.TEXT)
async def print_state(message: Message, state: FSMContext):
    await ReportsStates.print_state.set()

    if not await is_correct_command(state, message):
        return None

    if message.text == Button.SAVE:
        await message.answer(f'Пока не работает')
        return None

    data = await state.get_data()
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.HOME]
    rkb.add(*buttons)
    await state.update_data(buttons=buttons)
    await message.answer(data['result'], reply_markup=rkb)







