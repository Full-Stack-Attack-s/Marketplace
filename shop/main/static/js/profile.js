// ============================================
// PROFILE.JS — логика профиля
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // ── Автоматическая загрузка аватара с превью ──
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                const label = this.closest('.profile-field').querySelector('label');
                const previewContainer = label.querySelector('div');
                
                reader.onload = (e) => {
                    if (previewContainer) {
                        previewContainer.innerHTML = `<img src="${e.target.result}" style="width: 100%; height: 100%; object-fit: cover;">`;
                    }
                    // Отправляем форму после короткой задержки, чтобы пользователь увидел превью
                    setTimeout(() => {
                        this.closest('form').submit();
                    }, 500);
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});
