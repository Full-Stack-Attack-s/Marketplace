function handleStatusChange(select, orderId) {
    if (select.value === 'cancelled') {
        const reason = prompt("Пожалуйста, укажите причину отмены заказа:");
        if (reason && reason.trim() !== "") {
            document.getElementById('reason-' + orderId).value = reason;
            select.form.submit();
        } else {
            // Сбрасываем выбор, если причина не указана
            select.selectedIndex = 0;
            if (typeof showToast === 'function') {
                showToast("⚠️ Причина отмены обязательна", "error");
            } else {
                alert("⚠️ Причина отмены обязательна");
            }
        }
    } else {
        select.form.submit();
    }
}
