import os
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

# Создаем роутер, в который будем регистрировать хэндлеры
router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Вызываем функцию из нашего модуля базы данных
    db.add_user(tg_id=message.from_user.id, username=message.from_user.username)
    
    # Достаем URL из переменных окружения Render (или локального .env)
    url_vercel = os.getenv("URL_VERCEL")

    inline_btn = InlineKeyboardButton(
        text="Открыть Mini App 🚀",
        web_app=WebAppInfo(url=url_vercel)
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_btn]])

    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        f"Данные сохранены в базе данных.\n"
        f"Нажми кнопку для запуска приложения:",
        reply_markup=keyboard
    )