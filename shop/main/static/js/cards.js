// Переключение главного фото при клике на миниатюру
document.addEventListener('DOMContentLoaded', function() {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('mainImageSrc');

    if (!thumbnails.length || !mainImage) return;

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Убираем active у всех миниатюр
            thumbnails.forEach(t => t.classList.remove('active'));
            // Добавляем active текущей
            this.classList.add('active');
            // Меняем главное фото
            const newImageSrc = this.getAttribute('data-image');
            if (newImageSrc) {
                // Безопасный способ: создаём новый URL объект
                try {
                    const url = new URL(newImageSrc, window.location.origin);
                    // Проверяем, что это изображение (разрешаем только jpg, png, webp, gif)
                    if (url.pathname.match(/\.(jpg|jpeg|png|webp|gif)$/i)) {
                        mainImage.src = url.href;
                    }
                } catch(e) {
                    // Если невалидный URL, пробуем как относительный
                    if (newImageSrc.match(/^\/[a-zA-Z0-9\/\-_.]+\.(jpg|jpeg|png|webp|gif)$/i)) {
                        mainImage.src = newImageSrc;
                    }
                }
            }
        });
    });
});



    // Функция для корзины (если у вас уже есть addToCart, не переопределяйте)
    window.addToCart = window.addToCart || function(variantId) {
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken')
            },
            body: JSON.stringify({ variant_id: variantId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Товар добавлен в корзину');
            } else {
                alert('❌ Ошибка: ' + (data.error || 'попробуйте позже'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Ошибка добавления в корзину');
        });
    };



window.addToFavorites = function(productId, btnElement) {
    fetch(`/favorite/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Используем вашу функцию getCookie, которая уже есть в файле
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.status === 403 || response.redirected) {
            window.location.href = '/accounts/login/'; // Перенаправляем неавторизованных
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (data && data.status === 'ok') {
            // Если мы передали саму кнопку при клике, меняем её внешний вид
            if (btnElement) {
                if (data.is_favorite) {
                    btnElement.innerHTML = '❤️ В избранном';
                    btnElement.classList.add('active');
                } else {
                    btnElement.innerHTML = '🤍 В избранное';
                    btnElement.classList.remove('active');
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Ошибка добавления в избранное');
    });
};