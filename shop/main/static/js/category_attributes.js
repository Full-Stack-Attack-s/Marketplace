document.addEventListener("DOMContentLoaded", function() {
    const categorySelect = document.getElementById("id_category");
    const attributesContainer = document.getElementById("dynamic-attributes-container");

    if (categorySelect) {
        categorySelect.addEventListener("change", function() {
            const categoryId = this.value;
            attributesContainer.innerHTML = ''; // Очищаем контейнер

            if (categoryId) {
                fetch(`/api/category-attributes/${categoryId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.length > 0) {
                            let html = '<h4 class="mb-15">Специфичные характеристики</h4>';
                            data.forEach(attr => {
                                const requiredObj = attr.is_required ? 'required' : '';
                                const reqLabel = attr.is_required ? '*' : '';
                                
                                html += `
                                    <div class="form-group">
                                        <label>${attr.name} <span class="text-danger">${reqLabel}</span></label>
                                        <input type="text" name="attr_${attr.name}" ${requiredObj} 
                                            class="auth-form input" 
                                            class="dynamic-attr-input"
                                            placeholder="Введите значение...">
                                    </div>
                                `;
                            });
                            attributesContainer.innerHTML = html;
                        }
                    })
                    .catch(error => console.error('Ошибка загрузки атрибутов:', error));
            }
        });
    }
});
