import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher

# Импортируем ВСЕ функции из базы данных
from database.db import get_categories, get_products, get_subcategories, get_user_data_db, search_products
from handlers import register_all_handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем FastAPI
app = FastAPI()

# Настройка CORS политики для фронтенда на Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# ЭНДПОИНТЫ API ДЛЯ ВЕБ-ПРИЛОЖЕНИЯ
# =====================================================================

@app.get("/")
def root():
    """Эндпоинт для проверки работоспособности (Health Check) на Render"""
    return {"status": "alive", "message": "H1tle Shop Backend is running"}


@app.get("/api/user/{tg_id}")
def get_user_data(tg_id: int):
    """Получение данных пользователя (баланс и юзернейм)"""
    try:
        user = get_user_data_db(tg_id)
        if user:
            return {"status": "success", "username": user["username"], "balance": user["balance"]}
        return {"status": "error", "message": "User not found"}
    except Exception as e:
        logging.error(f"Ошибка в get_user_data: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/categories")
def fetch_categories():
    """Получение всех родительских категорий"""
    try:
        return get_categories()
    except Exception as e:
        logging.error(f"Ошибка в get_categories: {e}")
        return []


@app.get("/api/subcategories/{category_id}")
def fetch_subcategories(category_id: int):
    """Получение подкатегорий конкретной категории"""
    try:
        return get_subcategories(category_id)
    except Exception as e:
        logging.error(f"Ошибка в get_subcategories: {e}")
        return []


@app.get("/api/products/{subcategory_id}")
def fetch_products(subcategory_id: int):
    """Получение товаров конкретной подкатегории"""
    try:
        return get_products(subcategory_id)
    except Exception as e:
        logging.error(f"Ошибка в get_products: {e}")
        return []


@app.get("/api/products/search")
def api_search_products(query: str = ""):
    """Глобальный поиск по товарам"""
    try:
        return search_products(query)
    except Exception as e:
        logging.error(f"Ошибка в api_search_products: {e}")
        return []


# =====================================================================
# ЗАПУСК СЛУЖБ
# =====================================================================

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        logging.error("Переменная BOT_TOKEN не найдена в переменных окружения!")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    register_all_handlers(dp)
    
    port = int(os.getenv("PORT", 10000))
    
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    
    print(f"Бот и FastAPI запускаются на порту {port}...")
    
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа принудительно остановлена пользователем.")