// ============================================
// CARDS.JS — карточка товара
// ============================================

document.addEventListener('DOMContentLoaded', function () {

    // ── Переключение главного фото ──────────────
    const thumbs    = document.querySelectorAll('.thumb');
    const mainImage = document.getElementById('mainImageSrc');

    thumbs.forEach(thumb => {
        thumb.addEventListener('click', function () {
            thumbs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const newSrc = this.getAttribute('data-image');
            if (newSrc && mainImage) {
                // Простая проверка безопасности: предотвращаем javascript: URL
                if (newSrc.trim().toLowerCase().startsWith('javascript:')) {
                    console.error('Invalid image source');
                    return;
                }
                mainImage.style.opacity = '0';
                setTimeout(() => {
                    mainImage.setAttribute('src', newSrc);
                    mainImage.style.opacity = '1';
                }, 150);
            }
        });
    });

    // ── Зум при наведении на главное фото ───────
    const mainWrap = document.getElementById('mainImage');
    if (mainWrap && mainImage) {
        mainImage.style.transition = 'transform 0.35s ease, opacity 0.15s ease';
    }
});