function handleFavRemove(productId, btn) {
    if (typeof addToFavorites === 'function') {
        addToFavorites(null, productId, btn);
    }
    
    const card = document.getElementById('fav-item-' + productId);
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'scale(0.8)';
        setTimeout(() => {
            card.remove();
            const remainingCards = document.querySelectorAll('.fav-card');
            if (remainingCards.length === 0) {
                location.reload();
            }
            
            // Update counter text
            const countEl = document.querySelector('.fav-count');
            if (countEl) {
                countEl.textContent = remainingCards.length + ' товаров';
            }
        }, 300);
    }
}
