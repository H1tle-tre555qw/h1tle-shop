import sqlite3
from supabase import create_client

# 1. Настройки подключения к Supabase
SUPABASE_URL = "https://rwurajeiitptiqleqwmv.supabase.co"
# Сюда вставьте ваш секретный SERVICE_ROLE_KEY (не anon_key!) из Настройки -> Ключи API
SUPABASE_KEY = "sb_secret_2W8Pa3rt2lrfnoq6BgugCw_rnofRC-u" 

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Подключение к вашей локальной SQLite
# Используем путь database/shop.db, так как запускаем из корня проекта
DB_PATH = "database/shop.db"

def migrate_table(table_name: str):
    """Функция для автоматического переноса одной таблицы"""
    print(f"Перенос таблицы '{table_name}'...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Читаем все данные из SQLite
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"⚠️ Таблица '{table_name}' пуста в SQLite. Пропускаем.")
            return

        # Конвертируем строки в список словарей для Supabase
        data_to_insert = [dict(row) for row in rows]
        
        # Отправляем пачкой в Supabase
        result = supabase.table(table_name).insert(data_to_insert).execute()
        print(f"✅ Успешно перенесено строк в '{table_name}': {len(data_to_insert)}")
        
    except Exception as e:
        print(f"❌ Ошибка при переносе таблицы '{table_name}': {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== НАЧАЛО МИГРАЦИИ В SUPABASE ===")
    
    # Порядок важен из-за Foreign Key связей! Сначала категории, потом подкатегории, потом товары.
    migrate_table("users")
    migrate_table("categories")
    migrate_table("subcategories")
    migrate_table("products")
    
    print("=== МИГРАЦИЯ ЗАВЕРШЕНА ===")