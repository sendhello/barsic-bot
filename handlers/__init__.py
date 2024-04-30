from aiogram import Router

from constants import ADMIN_KEY, USER_KEY
from filters.auth import PermissionFilter
from filters.chat_type import ChatTypeFilter
from middlewares.blocked_user import BlockerUserMiddleware

from .info_menu import info_menu
from .main_menu import main_menu
from .report_menu import report_menu
from .service_distribution_menu import router as service_distribution_router
from .start import router as start_router


router = Router()
router.include_router(start_router)
router.include_router(main_menu)

admin_router = Router()
admin_router.include_router(report_menu)
admin_router.include_router(service_distribution_router)
admin_router.message.filter(PermissionFilter(roles=[ADMIN_KEY]))
admin_router.callback_query.filter(PermissionFilter(roles=[ADMIN_KEY]))
router.include_router(admin_router)

user_router = Router()
user_router.include_router(info_menu)
user_router.message.filter(PermissionFilter(roles=[ADMIN_KEY, USER_KEY]))
user_router.callback_query.filter(PermissionFilter(roles=[ADMIN_KEY, USER_KEY]))
router.include_router(user_router)

router.message.middleware.register(BlockerUserMiddleware())
router.message.filter(ChatTypeFilter(chat_type="private"))
