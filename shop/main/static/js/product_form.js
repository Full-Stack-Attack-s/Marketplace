// ─── Динамические атрибуты по категории ────────────────────────
function initProductForm(config) {
    const SAVED_ATTRS = config.savedAttrs || {};
    
    document.addEventListener('DOMContentLoaded', function () {
        const categorySelect = document.querySelector('select[name="category"]');
        const attrSection    = document.getElementById('dynamic-attributes-container');
        const attrsGrid      = document.getElementById('attrs-grid');

        if (!categorySelect) return;

        function fetchAttributes() {
            const categoryId = categorySelect.value;
            if (!categoryId) {
                if (attrSection) attrSection.classList.add('hidden');
                if (attrsGrid) attrsGrid.innerHTML = '';
                return;
            }

            // Показываем индикатор загрузки
            if (attrsGrid) attrsGrid.innerHTML = '<div class="pf-loading">⏳ Загрузка характеристик...</div>';
            if (attrSection) attrSection.classList.remove('hidden');

            fetch(`/api/category-attributes/${categoryId}/`)
                .then(r => r.ok ? r.json() : Promise.reject(r.status))
                .then(data => {
                    if (!data.length) {
                        if (attrSection) attrSection.classList.add('hidden');
                        return;
                    }
                    if (attrsGrid) attrsGrid.innerHTML = '';
                    if (attrSection) attrSection.classList.remove('hidden');
                    
                    data.forEach(attr => {
                        const savedVal = SAVED_ATTRS[attr.label] || SAVED_ATTRS[attr.name] || '';
                        const div = document.createElement('div');
                        div.className = 'form-group';
                        
                        let inputHtml = '';
                        const inputName = `attr_${attr.label || attr.name}`;
                        const isRequired = attr.is_required ? 'required' : '';
                        const placeholder = `Например: ${attr.type === 'number' ? '10' : 'значение'}`;

                        if (attr.type === 'number') {
                            inputHtml = `<input type="number" step="any" name="${inputName}" value="${savedVal}" placeholder="${placeholder}" class="auth-form input" ${isRequired}>`;
                        } else if (attr.type === 'boolean' || attr.type === 'bool') {
                            const checked = (savedVal === 'true' || savedVal === '1' || savedVal === 'on' || savedVal === 'Yes' || savedVal === 'Да') ? 'checked' : '';
                            inputHtml = `
                                <label class="pf-checkbox-label">
                                    <input type="checkbox" name="${inputName}" ${checked} class="pf-checkbox">
                                    <span class="pf-checkbox-text">${savedVal === 'true' ? 'Да' : 'Нет'} (отметьте, если есть)</span>
                                </label>
                            `;
                        } else {
                            // По умолчанию текст
                            inputHtml = `<input type="text" name="${inputName}" value="${savedVal}" placeholder="${placeholder}" class="auth-form input" ${isRequired}>`;
                        }

                        div.innerHTML = `
                            <label>${attr.label || attr.name}
                                ${attr.is_required ? '<span class="pf-required">*</span>' : ''}
                            </label>
                            ${inputHtml}
                        `;
                        if (attrsGrid) attrsGrid.appendChild(div);
                    });
                })
                .catch(err => {
                    console.warn('Ошибка загрузки атрибутов:', err);
                    if (attrSection) attrSection.classList.add('hidden');
                });
        }

        categorySelect.addEventListener('change', fetchAttributes);
        fetchAttributes(); // Вызов при загрузке (для режима редактирования)
    });

    // ─── Drag-and-drop + превью нескольких фото ─────────────────────
    (function () {
        const dropzone    = document.getElementById('dropzone');
        const fileInput   = document.getElementById('id_images');
        const previewGrid = document.getElementById('previewGrid');

        if (!dropzone || !fileInput) return;

        // Клик по зоне открывает диалог
        dropzone.addEventListener('click', function (e) {
            if (e.target.tagName !== 'LABEL') fileInput.click();
        });

        // Drag over / leave
        dropzone.addEventListener('dragover', e => {
            e.preventDefault();
            dropzone.classList.add('pf-dropzone--active');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('pf-dropzone--active'));

        // Drop
        dropzone.addEventListener('drop', e => {
            e.preventDefault();
            dropzone.classList.remove('pf-dropzone--active');
            handleFiles(e.dataTransfer.files);
        });

        // File input change
        fileInput.addEventListener('change', () => handleFiles(fileInput.files));

        // Храним выбранные файлы (DataTransfer trick)
        let dt = new DataTransfer();

        function handleFiles(files) {
            const MAX_SIZE = 5 * 1024 * 1024; // 5 МБ
            Array.from(files).forEach(file => {
                if (!file.type.startsWith('image/')) return;
                if (file.size > MAX_SIZE) {
                    showDropzoneError(`«${file.name}» превышает 5 МБ`);
                    return;
                }
                if (dt.files.length >= 10) {
                    showDropzoneError('Максимум 10 фотографий');
                    return;
                }
                dt.items.add(file);
                addPreview(file, dt.files.length - 1);
            });
            fileInput.files = dt.files;
        }

        function addPreview(file, index) {
            const reader = new FileReader();
            reader.onload = e => {
                const card = document.createElement('div');
                card.className = 'pf-preview-card';
                card.dataset.index = index;
                card.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}">
                    ${index === 0 ? '<span class="pf-main-badge">Главная</span>' : ''}
                    <button type="button" class="pf-delete-photo" onclick="removePreview(this, ${index})" title="Убрать">×</button>
                    <div class="pf-preview-name">${file.name}</div>
                `;
                if (previewGrid) previewGrid.appendChild(card);
            };
            reader.readAsDataURL(file);
        }

        window.removePreview = function(btn, removeIndex) {
            const card = btn.closest('.pf-preview-card');
            if (card) card.remove();

            // Перестраиваем DataTransfer без удалённого файла
            const newDt = new DataTransfer();
            Array.from(dt.files).forEach((f, i) => {
                if (i !== removeIndex) newDt.items.add(f);
            });
            dt = newDt;
            fileInput.files = dt.files;

            // Переиндексация и обновление бейджа "Главная"
            document.querySelectorAll('.pf-preview-card').forEach((c, i) => {
                c.dataset.index = i;
                const badge = c.querySelector('.pf-main-badge');
                if (i === 0 && !badge) {
                    const b = document.createElement('span');
                    b.className = 'pf-main-badge';
                    b.textContent = 'Главная';
                    c.insertBefore(b, c.querySelector('button'));
                } else if (i !== 0 && badge) {
                    badge.remove();
                }
            });
        };

        function showDropzoneError(msg) {
            const el = document.createElement('div');
            el.className = 'pf-dropzone-error';
            el.textContent = '⚠ ' + msg;
            if (dropzone) dropzone.after(el);
            setTimeout(() => el.remove(), 3500);
        }
    })();
}

// ─── Удаление существующих фото (AJAX) ──────────────────────────
window.deleteExistingPhoto = function(photoId, btn) {
    if (!confirm('Удалить фотографию?')) return;
    fetch(`/product/image/delete/${photoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            const card = document.getElementById(`photo-${photoId}`);
            if (card) card.remove();
        }
    })
    .catch(err => console.error('Ошибка удаления фото:', err));
};

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
