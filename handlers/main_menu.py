from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Start
from aiogram_dialog.widgets.text import Const, Format

from constants import ButtonID, text
from states import MainMenu, ReportMenu

main_menu = Dialog(
    Window(
        Format("Здравствуйте, {event.from_user.username}! \n\n" "Выберите действие\n"),
        Row(
            Start(
                Const(text(ButtonID.REPORTS)),
                id=ButtonID.REPORTS,
                state=ReportMenu.START,
            )
        ),
        state=MainMenu.START,
    )
)
