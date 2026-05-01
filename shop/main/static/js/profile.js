// ============================================
// PROFILE.JS — логика профиля (с обрезкой фото)
// ============================================

let cropper = null;

document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    const cropperModal = document.getElementById('cropperModal');
    const cropperImage = document.getElementById('cropperImage');

    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    // Показываем модалку и инициализируем кроппер
                    cropperImage.src = e.target.result;
                    cropperModal.style.display = 'flex';
                    
                    if (cropper) {
                        cropper.destroy();
                    }
                    
                    cropper = new Cropper(cropperImage, {
                        aspectRatio: 1, // Квадрат для аватара
                        viewMode: 1,
                        dragMode: 'move',
                        autoCropArea: 1,
                        restore: false,
                        guides: true,
                        center: true,
                        highlight: false,
                        cropBoxMovable: true,
                        cropBoxResizable: true,
                        toggleDragModeOnDblclick: false,
                    });
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Закрытие модалки при клике вне контента
    if (cropperModal) {
        cropperModal.addEventListener('click', function(e) {
            if (e.target === cropperModal) {
                closeCropper();
            }
        });
    }
});

window.closeCropper = function() {
    const cropperModal = document.getElementById('cropperModal');
    const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
    if (cropperModal) cropperModal.style.display = 'none';
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    if (avatarInput) avatarInput.value = ''; // Сбрасываем выбор
};

window.saveCroppedAvatar = function() {
    if (!cropper) return;

    // Получаем холст с обрезанным изображением
    const canvas = cropper.getCroppedCanvas({
        width: 400, // Оптимальный размер для аватара
        height: 400
    });

    canvas.toBlob((blob) => {
        const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
        const form = avatarInput.closest('form');
        
        // Создаем новый файл из Blob
        // Важно: имя файла должно быть таким же, как если бы пользователь выбрал его сам
        const file = new File([blob], "cropped_avatar.jpg", { type: "image/jpeg" });
        
        // Используем DataTransfer чтобы подменить файл в инпуте
        // Это стандартный способ программно изменить input[type="file"]
        const dt = new DataTransfer();
        dt.items.add(file);
        avatarInput.files = dt.files;

        // Показываем превью в кружочке перед отправкой
        const label = avatarInput.closest('.profile-field').querySelector('label');
        const previewContainer = label.querySelector('div');
        if (previewContainer) {
            previewContainer.innerHTML = `<img src="${canvas.toDataURL('image/jpeg')}" style="width: 100%; height: 100%; object-fit: cover;">`;
        }

        // Закрываем модалку
        closeCropper();

        // Отправляем через AJAX
        const formData = new FormData(form);
        // Заменяем файл в FormData на наш обрезанный Blob
        formData.set('avatar', blob, 'avatar.jpg');
        formData.set('update_user', '1');

        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                console.log('Аватар успешно сохранен');
                if (typeof showToast === 'function') {
                    showToast('✅ Фото профиля обновлено!', 'success');
                }
            } else {
                if (typeof showToast === 'function') {
                    showToast('❌ Ошибка при сохранении', 'error');
                }
            }
        })
        .catch(err => {
            console.error('Ошибка сети:', err);
        });
    }, 'image/jpeg', 0.9);
};
