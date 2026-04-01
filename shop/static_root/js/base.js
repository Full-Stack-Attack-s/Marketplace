// Функция переключения темы
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

// Обновление иконки темы
function updateThemeIcon(theme) {
    const themeIcons = document.querySelectorAll('.theme-icon');
    themeIcons.forEach(icon => {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    });
}

// Применяем сохранённую тему при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Добавляем обработчики клика на кнопки смены темы
    const themeButtons = document.querySelectorAll('.theme-toggle');
    themeButtons.forEach(button => {
        button.addEventListener('click', toggleTheme);
    });
});


// ============================================
// БЕСКОНЕЧНАЯ ПРОКРУТКА
// ============================================

let isLoading = false;
let currentPage = 1;
const itemsPerPage = 10; // Количество товаров на страницу

// Функция загрузки товаров
async function loadProducts() {
    if (isLoading) return;

    isLoading = true;
    const loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.classList.add('show');

    try {
        // Здесь должен быть AJAX запрос к серверу
        // Пример:
        // const response = await fetch(`/api/products/?page=${currentPage}&limit=${itemsPerPage}`);
        // const data = await response.json();

        // Имитация задержки загрузки (удалите в продакшене)
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Добавьте новые товары в сетку
        // addProductsToGrid(data.products);

        currentPage++;

        // Если товаров больше нет, скрываем индикатор
        // if (data.hasMore === false) {
        //     loadingIndicator.style.display = 'none';
        // }

    } catch (error) {
        console.error('Ошибка загрузки товаров:', error);
    } finally {
        isLoading = false;
        loadingIndicator.classList.remove('show');
    }
}

// Функция добавления товаров в сетку
function addProductsToGrid(products) {
    const productsGrid = document.querySelector('.products-grid');
    if (!productsGrid) return;

    products.forEach(product => {
        const productCard = createProductCard(product);
        productsGrid.appendChild(productCard);
    });
}

// Создание карточки товара
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    card.innerHTML = `
        <div class="product-image">
            <img src="${product.image || '/static/img/no-image.jpg'}" alt="${product.name}">
        </div>
        <div class="product-info">
            <div class="product-price">${product.price} ₽</div>
            <div class="product-seller">${product.name}</div>
            <button class="add-to-cart" onclick="addToCart(${product.id})">
                <span class="cart-icon">🛒</span> В корзину
            </button>
        </div>
    `;

    return card;
}

// Observer для бесконечной прокрутки
function initInfiniteScroll() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !isLoading) {
                    loadProducts();
                }
            });
        },
        {
            root: null,
            rootMargin: '100px',
            threshold: 0.1
        }
    );

    // Наблюдаем за индикатором загрузки
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        observer.observe(loadingIndicator);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initInfiniteScroll();
});

// ============================================
// ДОБАВЛЕНИЕ В КОРЗИНУ
// ============================================
function addToCart(productId) {
    // Здесь должна быть логика добавления в корзину
    console.log('Товар добавлен:', productId);

    // Обновление счетчика корзины
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        const currentCount = parseInt(cartCount.textContent) || 0;
        cartCount.textContent = currentCount + 1;

        // Анимация
        cartCount.style.transform = 'scale(1.3)';
        setTimeout(() => {
            cartCount.style.transform = 'scale(1)';
        }, 200);
    }
}

// ============================================
// СМЕНА ТЕМЫ (если еще не добавлена)
// ============================================
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeIcons = document.querySelectorAll('.theme-icon');
    themeIcons.forEach(icon => {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    });
}

// Применяем сохраненную тему
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Добавляем обработчики на кнопки смены темы
    const themeButtons = document.querySelectorAll('.theme-toggle');
    themeButtons.forEach(button => {
        button.addEventListener('click', toggleTheme);
    });
});