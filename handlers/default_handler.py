from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from misc import dp
from misc import logger


@dp.message_handler(state='*')
async def incorrect_command(message: Message, state: FSMContext):
    logger.info(f"[{await state.get_state()}] Команда {message.text} определена как ошибочная")
    await message.reply('Неверная команда. \nПожалуйста, выберите действие, используя клавиатуру ниже.')
