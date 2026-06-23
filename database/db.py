import sqlite3
from config import DB_NAME


def init_db():
    # Параметр timeout=5.0 заставляет SQLite ждать до 5 секунд, если база занята, 
    # вместо того чтобы сразу падать с ошибкой 'database is locked'
    conn = sqlite3.connect(DB_NAME, timeout=5.0)
    cursor = conn.cursor()
    
    # Включаем режим WAL. Он позволяет читать базу даже во время записи в неё.
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Твоя старая таблица для пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        tg_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0
    )''')

    # 2. Таблица главных категорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )''')

    # 3. Таблица подкатегорий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subcategories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    )''')

    # 4. Таблица товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT,
        subcategory_id INTEGER NOT NULL,
        FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE CASCADE
    )''')

    # Наполнение тестовыми данными
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        print("База пуста, создаем тестовый каталог...")
        cursor.execute("INSERT INTO categories (name) VALUES ('Электроника'), ('Одежда')")
        
        cursor.execute("INSERT INTO subcategories (name, category_id) VALUES ('Смартфоны', 1), ('Ноутбуки', 1)")
        cursor.execute("INSERT INTO subcategories (name, category_id) VALUES ('Футболки', 2), ('Худи', 2)")

        products = [
            ('iPhone 15', 'Флагманский смартфон', 999.99, '', 1),
            ('MacBook Air M2', 'Легкий ноутбук', 1299.00, '', 2),
            ('Черная футболка', '100% хлопок', 25.00, '', 3),
            ('Зимнее Худи', 'Теплое', 49.99, '', 4)
        ]
        cursor.executemany("INSERT INTO products (name, description, price, image_url, subcategory_id) VALUES (?, ?, ?, ?, ?)", products)

    conn.commit()
    conn.close()
    print("Новая база данных успешно инициализирована!")


def add_user(tg_id: int, username: str):
    """Добавление пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO users (tg_id, username) VALUES (?, ?)", 
            (tg_id, username)
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка БД: {e}")
    finally:
        conn.close()


def get_categories():
    """Получает список всех главных категорий из базы данных."""
    # Устанавливаем соединение с файлом базы данных
    conn = sqlite3.connect(DB_NAME)  
    
    # row_factory = sqlite3.Row позволяет возвращать строки из БД не в виде простых кортежей (типа (1, 'Электроника')),
    # а в виде объектов, похожих на словари, где можно обращаться к данным по именам колонок: row['name']
    conn.row_factory = sqlite3.Row   
    cursor = conn.cursor()
    
    # Выполняем SQL-запрос: выбрать id и name из таблицы categories
    cursor.execute("SELECT id, name FROM categories")
    rows = cursor.fetchall()  # Получаем все найденные строки
    
    conn.close()  # Обязательно закрываем соединение с базой
    
    # dict(row) превращает каждую строку SQLite в обычный Python-словарь: {'id': 1, 'name': 'Электроника'}
    # С помощью генератора списков [трансформация for переменная in список] собираем их в один красивый список
    return [dict(row) for row in rows]


def get_subcategories(category_id: int):
    """Получает подкатегории, которые привязаны к конкретной главной категории (по её category_id)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Знак "?" — это безопасный плейсхолдер. Вместо него подставится значение переменной category_id.
    # Это защищает базу данных от злоумышленников (так называемых SQL-инъекций).
    # Переменная передается в кортеже: (category_id,) — запятая в конце обязательна, если элемент один!
    cursor.execute("SELECT id, name FROM subcategories WHERE category_id = ?", (category_id,))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]


def get_products(subcategory_id: int):
    """Получает все товары, принадлежащие конкретной подкатегории (по её subcategory_id)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Запрашиваем только нужные поля для карточки товара: id, название, описание, цену и ссылку на картинку
    cursor.execute(
        "SELECT id, name, description, price, image_url FROM products WHERE subcategory_id = ?", 
        (subcategory_id,)
    )
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]