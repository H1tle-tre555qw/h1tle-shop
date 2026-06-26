import os
import requests
import logging

# Настройка логирования, если оно не подтянулось из main.py
logging.basicConfig(level=logging.INFO)

def get_supabase_credentials():
    """Вспомогательная функция для получения доступов"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        logging.error("❌ КРИТИЧЕСКАЯ ОШИБКА: SUPABASE_URL или SUPABASE_KEY не заданы в Environment Variables!")
        return None, None
    return supabase_url.rstrip('/'), supabase_key


def add_user(tg_id: int, username: str):
    """Добавление или обновление пользователя в базе данных"""
    url_base, key = get_supabase_credentials()
    if not url_base:
        return False
        
    url = f"{url_base}/rest/v1/users"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"  # Позволяет перезаписывать данные при совпадении tg_id
    }
    
    # Формируем тело запроса. Замените имена колонок, если в БД они называются иначе!
    data = {
        "tg_id": tg_id,
        "username": username if username else f"user_{tg_id}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code in [200, 201]:
            return True
        logging.error(f"Ошибка при добавлении пользователя: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        logging.error(f"Исключение при добавлении пользователя: {e}")
        return False


def get_categories():
    """Получение всех родительских категорий"""
    url_base, key = get_supabase_credentials()
    if not url_base:
        return []
        
    url = f"{url_base}/rest/v1/categories?select=id,name"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        logging.error(f"Supabase вернул ошибку в get_categories: {response.status_code}")
        return []
    except Exception as e:
        logging.error(f"Исключение в get_categories: {e}")
        return []


def get_subcategories(category_id: int):
    """Получение подкатегорий конкретной категории"""
    url_base, key = get_supabase_credentials()
    if not url_base:
        return []
        
    # Фильтруем подкатегории по id родительской категории
    url = f"{url_base}/rest/v1/subcategories?category_id=eq.{category_id}&select=id,name"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        logging.error(f"Supabase вернул ошибку в get_subcategories: {response.status_code}")
        return []
    except Exception as e:
        logging.error(f"Исключение в get_subcategories: {e}")
        return []


def get_products(subcategory_id: int):
    """Получение товаров конкретной подкатегории"""
    url_base, key = get_supabase_credentials()
    if not url_base:
        return []
        
    # Фильтруем товары по id подкатегории
    url = f"{url_base}/rest/v1/products?subcategory_id=eq.{subcategory_id}&select=id,name,price,image_url"
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        logging.error(f"Supabase вернул ошибку в get_products: {response.status_code}")
        return []
    except Exception as e:
        logging.error(f"Исключение in get_products: {e}")
        return []