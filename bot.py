from aiogram import executor
from misc import dp
import handlers
from aiogram import Dispatcher

__all__ = ['handlers']


async def shutdown(dispatcher: Dispatcher):
    print('shutdown')
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
