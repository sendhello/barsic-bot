from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.filters.chat_member_updated import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, Message
from aiogram_dialog import DialogManager

from states import MainMenu


router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")

# Исключительно для примера!
# В реальной жизни используйте более надёжные
# источники айди юзеров
users = {111, 222}


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    users.discard(event.from_user.id)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    users.add(event.from_user.id)


@router.message(StateFilter(None), CommandStart())
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenu.START)


@router.message(StateFilter(None))
async def reports(message: Message, state: FSMContext):
    await message.reply("Неверная команда")


@router.message(StateFilter(None), Command("help"))
async def help_command(message: Message):
    await message.answer("Для отображения списака комманд - выполните команду /set_commands и перезапустите телеграмм")
