// ============================================
// PROFILE.JS — логика профиля
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // ── Автоматическая загрузка аватара с превью ──
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
                // Сначала спрашиваем подтверждение
                if (confirm('Обновить фотографию профиля?')) {
                    const reader = new FileReader();
                    const label = this.closest('.profile-field').querySelector('label');
                    const previewContainer = label.querySelector('div');
                    
                    reader.onload = (e) => {
                        if (previewContainer) {
                            previewContainer.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; object-fit: cover;">`;
                        }
                        // Отправляем форму после короткой задержки
                        setTimeout(() => {
                            this.closest('form').submit();
                        }, 500);
                    };
                    reader.readAsDataURL(this.files[0]);
                } else {
                    // Очищаем input, чтобы можно было выбрать тот же файл снова
                    this.value = '';
                }
        });
    }
});
