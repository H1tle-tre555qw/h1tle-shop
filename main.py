import asyncio
import logging
import os  # Импортируем os для чтения переменных окружения
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import get_categories, get_products, get_subcategories
from handlers import register_all_handlers
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)

# Инициализируем FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем Supabase для использования в API эндпоинтах
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Обновленный эндпоинт пользователя (теперь читает из Supabase)
@app.get("/api/user/{tg_id}")
async def get_user_data(tg_id: int):
    try:
        response = supabase.table("users").select("username, balance").eq("tg_id", tg_id).execute()
        if response.data:
            user = response.data[0]
            return {"status": "success", "username": user["username"], "balance": user["balance"]}
        return {"status": "error", "message": "User not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ЭНДПОИНТЫ ДЛЯ МНОГОУРОВНЕВОГО КАТАЛОГА
@app.get("/api/categories")
async def fetch_categories():
    return get_categories()  # Убедитесь, что внутри функции get_categories теперь запрос к Supabase!

@app.get("/api/subcategories/{category_id}")
async def fetch_subcategories(category_id: int):
    return get_subcategories(category_id)

@app.get("/api/products/{subcategory_id}")
async def fetch_products(subcategory_id: int):
    return get_products(subcategory_id)


async def main():
    # init_db() # Локальный SQLite больше инициализировать не нужно
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    register_all_handlers(dp)
    
    # Динамически берём порт, который даёт Render, или 10000 для локальных тестов
    port = int(os.getenv("PORT", 10000))
    
    # host="0.0.0.0" обязателен для деплоя!
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
        print("Программа остановлена.")