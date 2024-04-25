from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from constants import PERMISSION_ID
from repositories.redis_repo import get_redis_repo
from states import MainMenu, ReportMenu, ServiceDistributionMenu


router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")

NOT_TEXT_STATES = [MainMenu.START, *list(ReportMenu), *list(ServiceDistributionMenu)]


@router.message(StateFilter(None), CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    redis_repo = await get_redis_repo()
    permission = await redis_repo.get_from_cache(key=f"{PERMISSION_ID}:{user_id}")
    if permission is None:
        await dialog_manager.start(MainMenu.AUTHORIZATION)
        return None

    await dialog_manager.start(MainMenu.START)


@router.message(StateFilter(*NOT_TEXT_STATES))
async def reports(message: Message, state: FSMContext):
    await message.reply("Неверная команда")


@router.message(StateFilter(None), Command("help"))
async def help_command(message: Message):
    await message.answer("Для отображения списака комманд - выполните команду /set_commands и перезапустите телеграмм")
