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

    // --- Дерево категорий: Раскрытие/Свертывание ---
    const toggles = document.querySelectorAll('.tree-toggle');
    toggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const node = this.closest('.tree-node');
            if (node) {
                node.classList.toggle('expanded');
            }
        });
    });

    // Авто-раскрытие дерева, если выбрана подкатегория
    const selectedRadio = document.querySelector('.mptt-tree input[type="radio"]:checked');
    if (selectedRadio) {
        let parent = selectedRadio.closest('.tree-node');
        // Раскрываем всех родителей
        while (parent) {
            parent.classList.add('expanded');
            const parentList = parent.parentElement; // <ul>
            if (parentList) {
                parent = parentList.closest('.tree-node');
            } else {
                parent = null;
            }
        }
    }
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
// ДОБАВЛЕНИЕ В КОРЗИНУ И ИЗБРАННОЕ
// ============================================

window.addToCart = function (variantId) {
    if (!variantId || variantId === 'None') {
        showToast('❌ Товар недоступен для добавления в корзину', 'error');
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');

    fetch('/cart/add/' + variantId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            showToast('✅ Товар добавлен в корзину!', 'success');
            // Обновляем счётчик везде
            document.querySelectorAll('.cart-count').forEach(el => {
                el.textContent = data.cart_count || (parseInt(el.textContent || 0) + 1);
                
                // Анимация
                el.style.transform = 'scale(1.3)';
                setTimeout(() => {
                    el.style.transform = 'scale(1)';
                }, 200);
            });
        } else {
            showToast('❌ Не удалось добавить товар', 'error');
        }
    })
    .catch(() => showToast('❌ Ошибка сети. Попробуйте ещё раз', 'error'));
};

window.addToFavorites = function (event, productId, btnElement) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');

    fetch(`/favorite/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(r => {
        if (r.status === 403 || r.redirected) {
            window.location.href = '/accounts/login/';
            return null;
        }
        return r.json();
    })
    .then(data => {
        if (!data) return;
        if (data.status === 'ok') {
            const buttons = document.querySelectorAll(`[data-id="${productId}"]`);
            buttons.forEach(btn => {
                const isMainCard = btn.classList.contains('btn-favorite'); // Большая кнопка
                if (data.is_favorite) {
                    btn.innerHTML = isMainCard ? '❤️ В избранном' : '❤️';
                    btn.classList.add('active');
                } else {
                    btn.innerHTML = isMainCard ? '🤍 В избранное' : '🤍';
                    btn.classList.remove('active');
                }
            });

            // Обновляем глобальный счетчик избранного
            document.querySelectorAll('.fav-badge').forEach(el => {
                if (data.favorites_count !== undefined) {
                    el.textContent = data.favorites_count;
                    el.style.display = data.favorites_count > 0 ? 'flex' : 'none';
                    
                    // Анимация
                    el.style.transform = 'scale(1.3)';
                    setTimeout(() => { el.style.transform = 'scale(1)'; }, 200);
                }
            });

            showToast(data.is_favorite ? '❤️ Добавлено в избранное' : '🤍 Убрано из избранного', 'info');
        }
    })
    .catch(() => showToast('❌ Ошибка. Попробуйте позже', 'error'));
};

// ── Toast-уведомления ─────────────────────────
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed; bottom: 24px; right: 24px;
            display: flex; flex-direction: column; gap: 10px;
            z-index: 9999; pointer-events: none;
        `;
        document.body.appendChild(container);
    }

    const colors = {
        success: 'rgba(102,217,168,0.95)',
        error:   'rgba(255,71,87,0.95)',
        info:    'rgba(30,41,59,0.92)'
    };

    const toast = document.createElement('div');
    toast.style.cssText = `
        padding: 12px 20px;
        border-radius: 12px;
        background: ${colors[type] || colors.info};
        color: #fff;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        pointer-events: auto;
        transform: translateX(120%);
        transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1);
        max-width: 300px;
        backdrop-filter: blur(8px);
    `;
    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
    });

    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ── CSRF ──────────────────────────────────────
function getCookie(name) {
    let v = null;
    if (document.cookie) {
        document.cookie.split(';').forEach(c => {
            c = c.trim();
            if (c.startsWith(name + '=')) v = decodeURIComponent(c.slice(name.length + 1));
        });
    }
    return v;
}