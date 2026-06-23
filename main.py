import asyncio
import logging
import uvicorn  # Импортируем uvicorn для запуска веб-сервера
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import get_categories, get_products, get_subcategories, init_db, DB_NAME
import sqlite3
from handlers import register_all_handlers


logging.basicConfig(level=logging.INFO)

# 1. Инициализируем FastAPI
app = FastAPI()

# Настраиваем CORS, чтобы наш сайт с Vercel (другой домен) мог делать запросы к нашему серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретно свой домен Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Создаем эндпоинт (API) для получения данных пользователя
@app.get("/api/user/{tg_id}")
async def get_user_data(tg_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, balance FROM users WHERE tg_id = ?", (tg_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"status": "success", "username": row[0], "balance": row[1]}
    return {"status": "error", "message": "User not found"}

# ==========================================
# ЭНДПОИНТЫ ДЛЯ МНОГОУРОВНЕВОГО КАТАЛОГА
# ==========================================

# @app.get указывает FastAPI, что этот адрес реагирует на GET-запросы (запросы на получение данных)
@app.get("/api/categories")
async def fetch_categories():
    """Отдает клиенту (HTML-странице) список всех главных категорий."""
    # Вызываем функцию из db.py и сразу возвращаем результат
    return get_categories()


# В фигурных скобках {category_id} указана переменная. 
# Если зайти на /api/subcategories/1, то FastAPI поймет, что category_id равен 1.
@app.get("/api/subcategories/{category_id}")
async def fetch_subcategories(category_id: int):
    """Отдает список подкатегорий для конкретной выбранной категории."""
    # Передаем полученный из ссылки ID в функцию базы данных
    return get_subcategories(category_id)


@app.get("/api/products/{subcategory_id}")
async def fetch_products(subcategory_id: int):
    """Отдает список товаров для конкретной выбранной подкатегории."""
    # Передаем полученный из ссылки ID подкатегории, чтобы отфильтровать товары
    return get_products(subcategory_id)


async def main():
    init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    register_all_handlers(dp)
    
    # 3. Настраиваем конфигурацию uvicorn сервера
    # Сервер будет слушать порт 8000 локально
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    
    print("Бот и FastAPI успешно запущены!")
    
    # Запускаем бота и сервер параллельно
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа остановлена.")