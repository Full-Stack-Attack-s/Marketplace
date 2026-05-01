// ============================================
// CART.JS — логика корзины
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const csrfTokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfToken = csrfTokenEl ? csrfTokenEl.value : '';

    window.changeQty = async function(itemId, delta) {
        const input = document.getElementById('qty-input-' + itemId);
        if (!input) return;
        
        let newQty = parseInt(input.value) + delta;
        if (newQty < 1) return;

        try {
            const response = await fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ quantity: newQty })
            });
            const data = await response.json();
            if (data.status === 'ok') {
                input.value = newQty;
                
                const itemTotalEl = document.getElementById('item-total-' + itemId);
                const subtotalEl = document.getElementById('summary-subtotal');
                const totalEl = document.getElementById('summary-total');
                
                if (itemTotalEl) itemTotalEl.innerText = Math.round(data.item_total) + ' ₽';
                if (subtotalEl) subtotalEl.innerText = Math.round(data.total_price) + ' ₽';
                if (totalEl) totalEl.innerText = Math.round(data.total_price) + ' ₽';
                
                // Обновление глобального счетчика в хедере
                updateGlobalCartCount();
            }
        } catch (e) {
            console.error('Ошибка обновления количества:', e);
        }
    };

    window.removeFromCart = async function(itemId) {
        if (!confirm('Удалить товар из корзины?')) return;

        try {
            const response = await fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const data = await response.json();
            if (data.status === 'ok') {
                const itemRow = document.getElementById('cart-item-' + itemId);
                if (itemRow) itemRow.remove();
                
                if (data.cart_empty) {
                    location.reload();
                } else {
                    const subtotalEl = document.getElementById('summary-subtotal');
                    const totalEl = document.getElementById('summary-total');
                    const badge = document.querySelector('.cart-count-badge');
                    
                    if (subtotalEl) subtotalEl.innerText = Math.round(data.total_price) + ' ₽';
                    if (totalEl) totalEl.innerText = Math.round(data.total_price) + ' ₽';
                    if (badge) badge.innerText = parseInt(badge.innerText) - 1;
                    
                    updateGlobalCartCount();
                }
            }
        } catch (e) {
            console.error('Ошибка удаления из корзины:', e);
        }
    };
    
    function updateGlobalCartCount() {
        const badge = document.querySelector('.cart-count-badge');
        const globalCount = document.querySelector('.cart-count');
        if (badge && globalCount) {
            globalCount.textContent = badge.textContent;
        }
    }
});