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

let isLoading = false;п
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

window.addToFavorites = function(productId, btnElement) {
    // ВАЖНО: блокируем стандартное поведение.
    // Обычно карточка в каталоге - это ссылка. Если мы кликнем по сердечку,
    // нас не должно перекинуть на страницу товара.
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    fetch(`/favorite/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Функция getCookie должна быть доступна!
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.status === 403 || response.redirected) {
            window.location.href = '/accounts/login/';
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (data && data.status === 'ok') {
            if (btnElement) {
                // Для маленьких карточек в каталоге меняем только саму эмодзи/иконку
                if (data.is_favorite) {
                    btnElement.innerHTML = '❤️';
                    btnElement.classList.add('active');
                } else {
                    btnElement.innerHTML = '🤍';
                    btnElement.classList.remove('active');
                }
            }
        }
    })
    .catch(error => console.error('Error:', error));
};

/**
 * Получение CSRF-токена из куки (необходимо для POST-запросов в Django)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}t

/**
 * Универсальная функция для добавления/удаления товара из избранного
 * @param {Event} event - объект события клика
 * @param {number} productId - ID товара
 * @param {HTMLElement} btnElement - элемент кнопки, на которую нажали
 */
window.addToFavorites = function(event, productId, btnElement) {
    // Останавливаем всплытие события, чтобы клик по сердечку
    // не срабатывал как клик по ссылке на карточку товара
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    fetch(`/favorite/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        // Если сервер просит авторизацию (например, 403 или редирект на логин)
        if (response.status === 403 || response.redirected) {
            window.location.href = '/accounts/login/';
            return null;
        }
        return response.json();
    })
    // Внутри функции addToFavorites в base.js
    .then(data => {
        if (data && data.status === 'ok') {
            const buttons = document.querySelectorAll(`[data-id="${productId}"]`);
            buttons.forEach(btn => {
                const isMainCard = btn.classList.contains('btn-favorite'); // Большая кнопка
                if (data.is_favorite) {
                    btn.innerHTML = isMainCard ? '❤️ В избранном' : '❤️';
                    btn.classList.add('active');
                } else {
                    // Если кнопка в карточке товара - пишем текст, если в каталоге - только иконку
                    btn.innerHTML = isMainCard ? '🖤 В избранное' : '🖤';
                    btn.classList.remove('active');
                }
            });
        }
    })
    .catch(error => {
        console.error('Ошибка при работе с избранным:', error);
    });
};