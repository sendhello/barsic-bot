from aiogram import Router

from filters.chat_type import ChatTypeFilter

from .main_menu import main_menu
from .report_menu import report_menu
from .start import router as start_router
from .service_distribution_menu import router as service_distribution_router


router = Router()
router.include_router(start_router)
router.include_router(main_menu)
router.include_router(report_menu)
router.include_router(service_distribution_router)

router.message.filter(ChatTypeFilter(chat_type="private"))
