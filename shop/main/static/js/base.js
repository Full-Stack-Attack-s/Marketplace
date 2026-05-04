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

    // Авто-скрытие уведомлений
    setTimeout(function() {
        const alerts = document.querySelectorAll('.auto-hide');
        alerts.forEach(alert => {
            alert.style.transition = "opacity 0.6s ease, transform 0.6s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 600);
        });
    }, 5000);

    // --- Локация: Выбор и Карта ---
    const locationSelector = document.getElementById('locationSelector');
    const locationModal = document.getElementById('locationModal');
    const closeLocationModal = document.getElementById('closeLocationModal');
    const confirmLocationBtn = document.getElementById('confirmLocation');
    const manualLocationInput = document.getElementById('manualLocation');
    const currentLocationText = document.getElementById('currentLocation');

    let myMap, myPlacemark;
    
    function initMap() {
        if (myMap) return;
        
        ymaps.ready(() => {
            myMap = new ymaps.Map("map", {
                center: [55.7558, 37.6173], // Москва
                zoom: 14,
                controls: ['zoomControl', 'fullscreenControl', 'geolocationControl']
            });

            // Клик по карте
            myMap.events.add('click', function (e) {
                const coords = e.get('coords');
                placeMarker(coords);
            });
        });
    }

    function placeMarker(coords) {
        if (myPlacemark) {
            myPlacemark.geometry.setCoordinates(coords);
        } else {
            myPlacemark = new ymaps.Placemark(coords, {}, {
                preset: 'islands#blueDotIconWithCaption',
                draggable: true
            });
            myMap.geoObjects.add(myPlacemark);
            
            // Слушаем завершение перетаскивания
            myPlacemark.events.add('dragend', function() {
                getAddress(myPlacemark.geometry.getCoordinates());
            });
        }
        getAddress(coords);
    }

    function getAddress(coords) {
        const input = document.getElementById('manualLocation');
        if (input) {
            input.value = "";
            input.placeholder = "⌛ Определение адреса...";
        }

        ymaps.geocode(coords).then(function (res) {
            const firstGeoObject = res.geoObjects.get(0);
            if (firstGeoObject) {
                const address = firstGeoObject.getAddressLine() || 
                              firstGeoObject.properties.get('text') ||
                              firstGeoObject.properties.get('name');
                if (input) {
                    input.value = address;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            } else {
                if (input) input.placeholder = "📍 Адрес не найден, введите вручную";
            }
        }).catch(err => {
            console.error('Yandex Geocode Error:', err);
            if (input) input.placeholder = "❌ Ошибка сервиса (проверьте API-ключ)";
        });
    }

    if (locationSelector) {
        locationSelector.addEventListener('click', () => {
            locationModal.style.display = 'flex';
            setTimeout(initMap, 100);
        });
    }

    if (closeLocationModal) {
        closeLocationModal.addEventListener('click', () => {
            locationModal.style.display = 'none';
        });
    }

    if (confirmLocationBtn) {
        confirmLocationBtn.addEventListener('click', () => {
            const val = manualLocationInput.value.trim();
            if (val) {
                currentLocationText.textContent = val;
                localStorage.setItem('user_location', val);
                locationModal.style.display = 'none';
                showToast('📍 Местоположение сохранено', 'success');
            }
        });
    }

    // Восстанавливаем локацию
    const savedLoc = localStorage.getItem('user_location');
    if (savedLoc && currentLocationText) {
        currentLocationText.textContent = savedLoc;
    }

    // --- Живой поиск ---
    const searchForm = document.getElementById('headerSearchForm');
    const searchInput = document.getElementById('headerSearchInput');
    const liveResults = document.getElementById('liveSearchResults');

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            if (!searchInput.value.trim()) {
                e.preventDefault();
                showToast('🔍 Введите поисковый запрос', 'info');
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length > 2) {
                // Имитация живого поиска
                liveResults.style.display = 'block';
                liveResults.innerHTML = `
                    <div class="live-search-item" onclick="location.href='/search/?q=${query}'">
                        🔍 Поиск «<strong>${query}</strong>» в каталоге
                    </div>
                `;
            } else {
                liveResults.style.display = 'none';
            }
        });

        // Скрывать результаты при клике вне
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !liveResults.contains(e.target)) {
                liveResults.style.display = 'none';
            }
        });
    }

    // --- Перевод (RU/EN) ---
    const langBtns = document.querySelectorAll('.lang-btn');
    const translations = {
        'RU': {
            'search_placeholder': 'Найти на BDSM-A',
            'catalog': 'Каталог',
            'cart': 'Корзина',
            'favorites': 'Избранное',
            'profile': 'Профиль'
        },
        'EN': {
            'search_placeholder': 'Find on BDSM-A',
            'catalog': 'Catalog',
            'cart': 'Cart',
            'favorites': 'Favorites',
            'profile': 'Profile'
        }
    };

    function switchLanguage(lang) {
        const t = translations[lang];
        if (!t) return;

        document.querySelectorAll('.search-input-field').forEach(i => i.placeholder = t.search_placeholder);
        document.querySelectorAll('.catalog-mobile, .catalog').forEach(el => {
            // У каталога есть псевдоэлемент, поэтому меняем текст хитро
            // Или просто меняем текст внутри если он там есть
        });
        
        localStorage.setItem('lang', lang);
        langBtns.forEach(btn => {
            btn.classList.toggle('active', btn.textContent === lang);
        });
        
        // В реальном приложении тут был бы i18next или Django i18n
        // Для демонстрации ограничимся этим
    }

    langBtns.forEach(btn => {
        btn.addEventListener('click', () => switchLanguage(btn.textContent));
    });

    const savedLang = localStorage.getItem('lang') || 'RU';
    switchLanguage(savedLang);

    // --- Отображение системных сообщений Django через Toast ---
    const djangoMessages = document.querySelectorAll('.messages-container .alert');
    djangoMessages.forEach(msg => {
        const text = msg.textContent.trim();
        const type = msg.classList.contains('alert-success') ? 'success' : 
                     (msg.classList.contains('alert-error') || msg.classList.contains('alert-danger')) ? 'error' : 'info';
        showToast(text, type);
        msg.remove(); // Удаляем из DOM, так как показали в Toast
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
// ДОБАВЛЕНИЕ В КОРЗИНУ И ИЗБРАННОЕ
// ============================================

window.addToCart = function (variantId, btnElement) {
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
            
            // Если передан элемент кнопки, превращаем его в селектор
            if (btnElement && !btnElement.closest('.quantity-selector')) {
                const parent = btnElement.parentElement;
                const qtySelector = document.createElement('div');
                qtySelector.className = 'quantity-selector';
                qtySelector.innerHTML = `
                    <button class="qty-btn minus" onclick="updateCartQty('${variantId}', -1, this)">-</button>
                    <span class="qty-value">1</span>
                    <button class="qty-btn plus" onclick="updateCartQty('${variantId}', 1, this)">+</button>
                `;
                btnElement.replaceWith(qtySelector);
            }

            // Обновляем счётчик
            updateCartCounter(data.cart_count);
        } else {
            showToast('❌ Не удалось добавить товар', 'error');
        }
    })
    .catch(() => showToast('❌ Ошибка сети. Попробуйте ещё раз', 'error'));
};

window.updateCartQty = function(variantId, delta, btn) {
    const qtySpan = btn.parentElement.querySelector('.qty-value');
    const parent = btn.parentElement.parentElement; // .product-info
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
    
    const formData = new FormData();
    formData.append('delta', delta);

    fetch('/cart/update-variant/' + variantId + '/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            if (data.removed) {
                // Возвращаем кнопку "В корзину"
                const addBtn = document.createElement('button');
                addBtn.className = 'add-to-cart';
                addBtn.onclick = () => addToCart(variantId, addBtn);
                addBtn.innerHTML = '🛒 В корзину';
                btn.parentElement.replaceWith(addBtn);
                showToast('🗑️ Удалено из корзины', 'info');
            } else {
                qtySpan.textContent = data.quantity;
            }
            updateCartCounter(data.cart_count);
        }
    })
    .catch(() => showToast('❌ Ошибка обновления', 'error'));
};

function updateCartCounter(count) {
    document.querySelectorAll('.cart-count').forEach(el => {
        el.textContent = count;
        el.style.transform = 'scale(1.3)';
        setTimeout(() => { el.style.transform = 'scale(1)'; }, 200);
    });
}

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

// ============================================
// ГЛОБАЛЬНАЯ ВАЛИДАЦИЯ ТЕЛЕФОНА (+7...)
// ============================================
document.addEventListener('input', function(e) {
    const el = e.target;
    if (el.name === 'phone' || el.name === 'phone_number') {
        el.setAttribute('maxlength', '12');
        let val = el.value;

        // Если пусто — ставим +7
        if (!val) {
            el.value = '+7';
            return;
        }

        // Если удалили +7 — возвращаем его
        if (!val.startsWith('+7')) {
            let digits = val.replace(/[^0-9]/g, '');
            // Если вставили номер с 7 или 8 в начале, убираем их перед приклеиванием +7
            if (digits.startsWith('7') || digits.startsWith('8')) {
                digits = digits.substring(1);
            }
            el.value = '+7' + digits;
        } else {
            // Разрешаем только цифры после префикса
            el.value = '+7' + val.substring(2).replace(/[^0-9]/g, '');
        }

        // Жесткое ограничение 12 символов
        if (el.value.length > 12) {
            el.value = el.value.substring(0, 12);
        }
    }
});

document.addEventListener('focusin', function(e) {
    const el = e.target;
    if ((el.name === 'phone' || el.name === 'phone_number') && !el.value) {
        el.value = '+7';
    }
});

document.addEventListener('blur', function(e) {
    const el = e.target;
    if (el.name === 'phone' || el.name === 'phone_number') {
        if (el.value.length > 2 && el.value.length < 12) {
            showToast('⚠️ Номер телефона должен содержать 11 цифр (+7...)', 'warning');
        }
    }
}, true);