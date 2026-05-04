document.addEventListener('DOMContentLoaded', function() {
    // --- Flatpickr для даты рождения ---
    const birthDateInput = document.getElementById('id_birth_date');
    if (birthDateInput) {
        const initialBirthDate = birthDateInput.value;
        flatpickr("#id_birth_date", {
            locale: "ru",
            dateFormat: "Y-m-d",
            allowInput: true,
            disableMobile: "true",
            onClose: function(selectedDates, dateStr, instance) {
                if (initialBirthDate && dateStr !== initialBirthDate) {
                    if (confirm('⚠️ Изменение даты рождения возможно только через службу поддержки. Перейти в чат поддержки?')) {
                        // Предполагаем, что URL передается через глобальную переменную или мы знаем его
                        window.location.href = "/chat/"; 
                        instance.setDate(initialBirthDate); 
                    } else {
                        instance.setDate(initialBirthDate);
                    }
                }
            }
        });
    }

    // --- Ограничение индекса только цифрами ---
    const zipInput = document.getElementById('id_zip_code');
    if (zipInput) {
        zipInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }

    // --- Логика аватара и кроппера (уже есть в profile.js, но дополним если нужно) ---
    // В profile_edit.html подключается и profile.js и этот файл.
});
