from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from misc import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class GeneralMenu(StatesGroup):
    main_menu_state = State()


@dp.message_handler(commands='start', state='*')
async def start_command(message: Message, state: FSMContext):
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = ['Отчеты', 'Помощь', 'Установить команды']
    rkb.add(*buttons)
    await message.answer('Выберите действие из меню', reply_markup=rkb)
    await state.update_data(buttons=list(map(str.lower, buttons)))
    await GeneralMenu.main_menu_state.set()


@dp.message_handler(commands=['help'], state='*')
async def help_command(message: Message):
    await message.answer('Для отображения списака комманд - выполните команду /set_commands и перезапустите телеграмм')
    await message.reply('Хееееелп!')


@dp.message_handler(commands='set_commands', state='*')
async def set_commands(message: Message):
    commands = [
        BotCommand(command="/start", description="Старт"),
        BotCommand(command="/help", description="Помощь"),
        # BotCommand(command="/food", description="Заказать блюда")
    ]
    await message.answer('Команды установлены. \nДля отображения списка комманд перезапустите приложение телеграм')
    await bot.set_my_commands(commands)

