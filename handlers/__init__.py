import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from constants import ADMIN_KEY, USER_KEY
from filters.auth import PermissionFilter
from filters.chat_type import ChatTypeFilter
from middlewares.blocked_user import BlockerUserMiddleware

from .info_menu import info_menu
from .main_menu import main_menu
from .report_menu import report_menu
from .service_distribution_menu import service_distribution_menu
from .start import router as start_router


logger = logging.getLogger(__name__)


router = Router()
router.include_router(start_router)
router.include_router(main_menu)

admin_router = Router()
admin_router.include_router(service_distribution_menu)
admin_router.message.filter(PermissionFilter(roles=[ADMIN_KEY]))
admin_router.callback_query.filter(PermissionFilter(roles=[ADMIN_KEY]))
router.include_router(admin_router)

user_router = Router()
user_router.include_router(info_menu)
user_router.include_router(report_menu)
user_router.message.filter(PermissionFilter(roles=[ADMIN_KEY, USER_KEY]))
user_router.callback_query.filter(PermissionFilter(roles=[ADMIN_KEY, USER_KEY]))
router.include_router(user_router)

router.message.middleware.register(BlockerUserMiddleware())
router.message.filter(ChatTypeFilter(chat_type="private"))


# @router.error(ExceptionTypeFilter(MyCustomException), F.update.message.as_("message"))
# async def handle_my_custom_exception(event: ErrorEvent, message: Message):
#     # do something with error
#     await message.answer("Oops, something went wrong!")


@router.error()
async def error_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)

    user_event = event.update.message or event.update.callback_query
    await user_event.answer(f"ERROR: {type(event.exception).__name__}: {event.exception}", show_alert=False)
