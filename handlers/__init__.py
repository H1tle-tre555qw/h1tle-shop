from aiogram import Dispatcher
from .users import router as users_router


def register_all_handlers(dp: Dispatcher):
    """Функция для автоматической регистрации всех роутеров проекта"""
    dp.include_router(users_router)