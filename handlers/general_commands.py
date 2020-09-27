from aiogram.dispatcher import FSMContext
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup

from constants import Button
from misc import dp, bot
from states import GeneralMenu


@dp.message_handler(commands='start', state='*')
@dp.message_handler(lambda message: message.text in [Button.CANCEL, Button.HOME], state='*')
async def start_command(message: Message, state: FSMContext):
    await GeneralMenu.general_menu_state.set()
    rkb = ReplyKeyboardMarkup(row_width=1)
    buttons = [Button.REPORTS, Button.HELP, Button.SET_COMMANDS]
    rkb.add(*buttons)
    await message.answer('Выберите действие из меню', reply_markup=rkb)


@dp.message_handler(commands=['help'], state='*')
@dp.message_handler(lambda message: message.text == Button.HELP, state=GeneralMenu.general_menu_state)
async def help_command(message: Message):
    await message.answer('Для отображения списака комманд - выполните команду /set_commands и перезапустите телеграмм')
    await message.reply('Хееееелп!')


@dp.message_handler(lambda message: message.text == Button.SET_COMMANDS, state=GeneralMenu.general_menu_state)
@dp.message_handler(commands='set_commands', state='*')
async def set_commands(message: Message):
    commands = [
        BotCommand(command="/start", description=Button.START),
        BotCommand(command="/set_commands", description=Button.SET_COMMANDS),
        BotCommand(command="/help", description=Button.HELP),
    ]
    await message.answer('Команды установлены. \nДля отображения списка комманд перезапустите приложение телеграм')
    await bot.set_my_commands(commands)

