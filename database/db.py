import os
from supabase import create_client, Client

# Инициализируем клиент Supabase
# В облаке Render эти переменные возьмутся из Environment Variables,
# а локально на ПК — из вашей системы или .env файла
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ (Таблица 'users')
# ==========================================

def add_user(tg_id: int, username: str, balance: int = 0):
    """
    Добавляет нового пользователя в базу данных Supabase.
    Если пользователь уже существует, ничего не делает (или обновляет username).
    """
    try:
        # Сначала проверяем, есть ли уже такой пользователь
        user_exists = supabase.table("users").select("tg_id").eq("tg_id", tg_id).execute()
        
        if not user_exists.data:
            # Если данных нет — создаем новую запись
            data = {
                "tg_id": tg_id,
                "username": username,
                "balance": balance
            }
            supabase.table("users").insert(data).execute()
            print(f"Пользователь {username} успешно добавлен в Supabase.")
        else:
            # Если пользователь есть, можно обновить его юзернейм (на случай, если он его изменил в Telegram)
            supabase.table("users").update({"username": username}).eq("tg_id", tg_id).execute()
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")


def update_user_balance(tg_id: int, amount: int):
    """
    Изменяет баланс пользователя (например, при покупке или пополнении).
    """
    try:
        # Получаем текущий баланс пользователя
        response = supabase.table("users").select("balance").eq("tg_id", tg_id).execute()
        if response.data:
            current_balance = response.data[0]["balance"]
            new_balance = current_balance + amount
            
            # Сохраняем новый баланс
            supabase.table("users").update({"balance": new_balance}).eq("tg_id", tg_id).execute()
            print(f"Баланс пользователя {tg_id} изменен на {amount}. Новый баланс: {new_balance}")
        else:
            print("Пользователь для обновления баланса не найден.")
    except Exception as e:
        print(f"Ошибка при обновлении баланса: {e}")


# ==========================================
# МНОГОУРОВНЕВЫЙ КАТАЛОГ ТОВАРОВ
# ==========================================

def get_categories():
    """Получает все главные категории из Supabase"""
    response = supabase.table("categories").select("id, name").execute()
    return response.data


def get_subcategories(category_id: int):
    """Получает подкатегории, отфильтрованные по ID главной категории"""
    response = supabase.table("subcategories").select("id, name, category_id").eq("category_id", category_id).execute()
    return response.data


def get_products(subcategory_id: int):
    """Получает товары, отфильтрованные по ID подкатегории"""
    response = supabase.table("products").select("id, name, description, price, subcategory_id").eq("subcategory_id", subcategory_id).execute()
    return response.data