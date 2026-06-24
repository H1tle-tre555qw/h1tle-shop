// Инициализация Telegram WebApp API
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Базовый URL вашего FastAPI бэкенда
const API_BASE_URL = "https://h1tle-shop.onrender.com"; 

// Состояние приложения
let currentScreen = "categories"; // "categories", "subcategories", "products"
let activeCategoryId = null;
let activeSubcategoryId = null;
let activeCategoryName = "Категории";
let activeSubcategoryName = "";
let cart = [];

// DOM Элементы
const grid = document.getElementById('content-grid');
const title = document.getElementById('main-title');
const backBtn = document.getElementById('back-btn');
const searchInput = document.getElementById('search-input');
const cartBtn = document.getElementById('cart-btn');
const cartCount = document.getElementById('cart-count');

// Инициализация данных пользователя из Telegram
if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
    const user = tg.initDataUnsafe.user;
    document.getElementById('username').innerText = user.username ? `@${user.username}` : user.first_name;
}
document.getElementById('balance-val').innerText = "2 500"; // Тут позже можно сделать динамический баланс из БД

// --- ГЛАВНАЯ ФУНКЦИЯ ОТРИСОВКИ ---
async function render() {
    grid.innerHTML = "<div style='grid-column: span 2; text-align:center;'>Загрузка...</div>"; 

    try {
        if (currentScreen === "categories") {
            title.innerText = "Категории";
            backBtn.style.display = "none";

            // Делаем запрос к эндпоинту категорий
            const response = await fetch(`${API_BASE_URL}/api/categories`);
            const categories = await response.json();
            
            grid.innerHTML = "";
            categories.forEach(cat => {
                // Так как картинок в таблице categories у нас нет, используем дефолтную иконку 📁
                grid.innerHTML += `
                    <div class="menu-card" data-id="${cat.id}" data-name="${cat.name}">
                        <div class="menu-icon">📁</div>
                        <div>${cat.name}</div>
                    </div>`;
            });

            // Навешиваем клики на созданные карточки категорий
            document.querySelectorAll('.menu-card').forEach(card => {
                card.addEventListener('click', () => {
                    activeCategoryId = card.getAttribute('data-id');
                    activeCategoryName = card.getAttribute('data-name');
                    currentScreen = "subcategories";
                    render();
                });
            });
        } 
        else if (currentScreen === "subcategories") {
            title.innerText = activeCategoryName;
            backBtn.style.display = "block";

            // Запрос подкатегорий по ID выбранной категории
            const response = await fetch(`${API_BASE_URL}/api/subcategories/${activeCategoryId}`);
            const subcategories = await response.json();

            grid.innerHTML = "";
            if (subcategories.length === 0) {
                grid.innerHTML = "<div style='grid-column: span 2; text-align:center;'>Тут пока ничего нет</div>";
                return;
            }

            subcategories.forEach(sub => {
                grid.innerHTML += `
                    <div class="menu-card sub-card" data-id="${sub.id}" data-name="${sub.name}">
                        <div class="menu-icon">📂</div>
                        <div>${sub.name}</div>
                    </div>`;
            });

            // Клик по подкатегории
            document.querySelectorAll('.sub-card').forEach(card => {
                card.addEventListener('click', () => {
                    activeSubcategoryId = card.getAttribute('data-id');
                    activeSubcategoryName = card.getAttribute('data-name');
                    currentScreen = "products";
                    render();
                });
            });
        } 
        else if (currentScreen === "products") {
            title.innerText = activeSubcategoryName;
            backBtn.style.display = "block";

            // Запрос товаров по ID выбранной подкатегории
            const response = await fetch(`${API_BASE_URL}/api/products/${activeSubcategoryId}`);
            const products = await response.json();

            grid.innerHTML = "";
            if (products.length === 0) {
                grid.innerHTML = "<div style='grid-column: span 2; text-align:center;'>Товары не найдены</div>";
                return;
            }

            products.forEach(prod => {
                // Используем ссылку из БД, если её нет — ставим заглушку-эмодзи 📦
                const imgHTML = prod.image_url && prod.image_url.startsWith('http') 
                    ? `<img src="${prod.image_url}" class="product-img" alt="${prod.name}">`
                    : `<div class="menu-icon">📦</div>`;

                grid.innerHTML += `
                    <div class="product-card">
                        ${imgHTML}
                        <div class="product-title">${prod.name}</div>
                        <div class="product-price">${prod.price} ₽</div>
                        <button class="btn-buy" data-name="${prod.name}">Купить</button>
                    </div>`;
            });

            // Навешиваем клики на кнопки «Купить»
            document.querySelectorAll('.btn-buy').forEach(btn => {
                btn.addEventListener('click', () => {
                    const productName = btn.getAttribute('data-name');
                    addToCart(productName);
                });
            });
        }
    } catch (error) {
        console.error("Ошибка загрузки данных с API:", error);
        grid.innerHTML = "<div style='grid-column: span 2; text-align:center; color:red;'>Ошибка загрузки данных</div>";
    }
}

// --- ЛОГИКА НАВИГАЦИИ НАЗАД ---
function goBack() {
    if (currentScreen === "products") {
        currentScreen = "subcategories";
    } else if (currentScreen === "subcategories") {
        currentScreen = "categories";
    }
    render();
}

// --- УПРАВЛЕНИЕ КОРЗИНОЙ ---
function addToCart(productName) {
    cart.push(productName);
    if (cart.length > 0) {
        cartBtn.style.display = 'flex';
        cartCount.innerText = Math.min(cart.length, 99);
    }
}

// --- ЖИВОЙ ПОИСК ---
function searchHandler() {
    const query = searchInput.value.toLowerCase();
    const cards = document.querySelectorAll('.menu-card, .product-card');

    cards.forEach(card => {
        const text = card.innerText.toLowerCase();
        card.style.display = text.includes(query) ? "flex" : "none";
    });
}

// --- НАЗНАЧЕНИЕ СОБЫТИЙ СЛУШАТЕЛЯМ ---
backBtn.addEventListener('click', goBack);
searchInput.addEventListener('input', searchHandler);

cartBtn.addEventListener('click', () => tg.showAlert(`В корзине товаров: ${cart.length}`));
document.getElementById('support-btn').addEventListener('click', () => tg.showAlert("Связь с поддержкой..."));
document.getElementById('reviews-btn').addEventListener('click', () => tg.showAlert("Отзывы клиентов..."));

// Первый запуск при открытии страницы
render();