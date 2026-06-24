import asyncio
import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from database.db import get_categories, get_products, get_subcategories
from handlers import register_all_handlers
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

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

# Подключаем Supabase с отключенным HTTP/2 во избежание ошибок StreamReset на Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
options = ClientOptions(http2=False)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options=options)


# =====================================================================
# ЭНДПОИНТЫ API ДЛЯ ВЕБ-ПРИЛОЖЕНИЯ (Синхронные во избежание блокировок)
# =====================================================================

@app.get("/")
def root():
    """Эндпоинт для проверки работоспособности (Health Check) на Render"""
    return {"status": "alive", "message": "H1tle Shop Backend is running"}


@app.get("/api/user/{tg_id}")
def get_user_data(tg_id: int):
    """Получение данных пользователя (баланс и юзернейм)"""
    try:
        response = supabase.table("users").select("username, balance").eq("tg_id", tg_id).execute()
        if response.data:
            user = response.data[0]
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
        logging.error(f"Ошибка in get_products: {e}")
        return []


# =====================================================================
# ЗАПУСК СЛУЖБ
# =====================================================================

async def main():
    # Достаем новый токен из панели Render (или из .env локально)
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        logging.error("Переменная BOT_TOKEN не найдена в переменных окружения!")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    register_all_handlers(dp)
    
    # Динамически берём порт, который выдает среда Render
    port = int(os.getenv("PORT", 10000))
    
    # Настройка конфигурации веб-сервера Uvicorn
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    
    print(f"Бот и FastAPI запускаются на порту {port}...")
    
    # Одновременный запуск Long Polling бота и веб-сервера API
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа принудительно остановлена пользователем.")