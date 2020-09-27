from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from callbacks import people_in_zone, total_report
from constants import Button
from library.aiogramcalendar import create_calendar
from misc import dp
from states import GeneralMenu, ReportsStates


@dp.message_handler(lambda message: message.text == Button.REPORTS, state=GeneralMenu.general_menu_state)
async def reports_menu_state(message: Message, state: FSMContext):
    await ReportsStates.reports_menu_state.set()
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.PEOPLE_IN_ZONE, Button.TOTAL_REPORT, Button.SUM_REPORT]
    rkb.add(*buttons)
    await message.answer('Выберите отчет', reply_markup=rkb)


@dp.message_handler(lambda message: message.text == Button.CHANGE_PERIOD, state=ReportsStates.set_period_state)
@dp.message_handler(lambda message: message.text == Button.CHANGE_PERIOD, state=ReportsStates.choose_date_from_state)
@dp.message_handler(lambda message: message.text == Button.CHANGE_PERIOD, state=ReportsStates.choose_date_to_state)
@dp.message_handler(
    lambda message: message.text in [Button.TOTAL_REPORT, Button.SUM_REPORT], state=ReportsStates.reports_menu_state)
async def choose_period_state(message: Message, state: FSMContext):
    await ReportsStates.choose_period_state.set()

    if message.text in [Button.TOTAL_REPORT, Button.SUM_REPORT]:
        await state.update_data(report_name=message.text)

    memory = await state.get_data()
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.TODAY, Button.YESTERDAY, Button.OTHER_PERIOD]
    rkb.add(*buttons)
    await message.answer(f"Выберите период отчета {memory['report_name']}", reply_markup=rkb)


@dp.message_handler(lambda message: message.text == Button.OTHER_PERIOD, state=ReportsStates.choose_period_state)
async def choose_date_from_state(message: Message, state: FSMContext):
    await ReportsStates.choose_date_from_state.set()

    await state.update_data(message=message)
    await message.answer("Выберите начало периода:", reply_markup=ReplyKeyboardRemove())
    await message.answer("------------------------", reply_markup=create_calendar())


@dp.message_handler(lambda message: message.text in [Button.TODAY, Button.YESTERDAY], state=ReportsStates.choose_period_state)
@dp.message_handler(lambda message: message.text == Button.PEOPLE_IN_ZONE, state=ReportsStates.reports_menu_state)
@dp.message_handler(lambda message: message.text == Button.SET, state=ReportsStates.choose_date_to_state)
async def set_period_state(message: Message, state: FSMContext):
    await ReportsStates.set_period_state.set()

    if message.text == Button.PEOPLE_IN_ZONE:
        await state.update_data(report_name=Button.PEOPLE_IN_ZONE)

    memory = await state.get_data()
    report_name = memory['report_name']

    date_from = date_to = None

    if message.text == Button.TODAY:
        date_from = date_to = datetime.now()
        await state.update_data(date_from=date_from.strftime('%Y%m%d'))
        await state.update_data(date_to=date_to.strftime('%Y%m%d'))

    elif message.text == Button.YESTERDAY:
        date_from = date_to = datetime.now() - timedelta(1)
        await state.update_data(date_from=date_from.strftime('%Y%m%d'))
        await state.update_data(date_to=date_to.strftime('%Y%m%d'))

    elif message.text == Button.SET:
        date_from = datetime.strptime(memory.get('date_from'), '%Y%m%d')
        date_to = datetime.strptime(memory.get('date_to'), '%Y%m%d')

    buttons = [Button.REQUEST, Button.CANCEL]
    message_text = f'Будет сформирован отчет {report_name}'

    if report_name != Button.PEOPLE_IN_ZONE:
        message_text += f" за {date_from.strftime('%d-%m-%Y')}" if date_from == date_to \
            else f' за период с {date_from.strftime("%d-%m-%Y")} по {date_to.strftime("%d-%m-%Y")}'
        buttons.append(Button.CHANGE_PERIOD)

    rkb = ReplyKeyboardMarkup(row_width=1)
    rkb.add(*buttons)
    await message.answer(message_text, reply_markup=rkb)


@dp.message_handler(lambda message: message.text == Button.REQUEST, state=ReportsStates.set_period_state)
async def request_state(message: Message, state: FSMContext):
    await ReportsStates.request_state.set()

    memory = await state.get_data()
    result = None

    if memory['report_name'] == Button.PEOPLE_IN_ZONE:
        result = await people_in_zone()

    elif memory['report_name'] == Button.TOTAL_REPORT:
        result = await total_report(
            date_from=datetime.strptime(memory['date_from'], '%Y%m%d'),
            date_to=datetime.strptime(memory['date_to'], '%Y%m%d'))

    elif memory['report_name'] == Button.SUM_REPORT:
        await message.answer(f'Функция временно не работает')

    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.PRINT, Button.SAVE]
    rkb.add(*buttons)
    await state.update_data(result=result)
    await message.answer(f'Отчет получен', reply_markup=rkb)


@dp.message_handler(lambda message: message.text == Button.PRINT, state=ReportsStates.request_state)
async def print_state(message: Message, state: FSMContext):
    await ReportsStates.print_state.set()

    memory = await state.get_data()
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.HOME]
    rkb.add(*buttons)
    await message.answer(memory['result'], reply_markup=rkb)


@dp.message_handler(lambda message: message.text == Button.SAVE, state=ReportsStates.request_state)
async def print_state(message: Message, state: FSMContext):
    await ReportsStates.save_state.set()
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.HOME]
    rkb.add(*buttons)
    await message.answer('Функция временно не работает', reply_markup=rkb)
