document.addEventListener('DOMContentLoaded', function() {
    const cardInput = document.getElementById('card_number');
    const checkoutForm = document.getElementById('checkout-form');
    const errorDiv = document.getElementById('card-error');

    if (cardInput) {
        cardInput.addEventListener('input', function(e) {
            // Formatting: 0000 0000 0000 0000
            let value = e.target.value.replace(/\D/g, '');
            let formatted = value.match(/.{1,4}/g)?.join(' ') || '';
            e.target.value = formatted.substring(0, 19);
            
            // Clear error while typing
            if (errorDiv) errorDiv.style.display = 'none';
            this.classList.remove('input-invalid');
        });
    }

    function validateLuhn(cardNumStr) {
        // Преобразуем строку в массив цифр (убираем пробелы)
        let cardNum = cardNumStr.replace(/\s+/g, '').split('').map(Number);
        
        // Алгоритм Луна
        for (let i = cardNum.length - 2; i >= 0; i -= 2) {
            cardNum[i] = cardNum[i] * 2;
            if (cardNum[i] > 9) {
                cardNum[i] = Math.floor(cardNum[i] / 10) + (cardNum[i] % 10);
            }
        }
        
        let cardSum = cardNum.reduce((a, b) => a + b, 0);
        return cardSum % 10 === 0;
    }

    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            if (cardInput) {
                const cardValue = cardInput.value;
                if (!validateLuhn(cardValue)) {
                    e.preventDefault();
                    if (errorDiv) errorDiv.style.display = 'block';
                    cardInput.classList.add('input-invalid');
                    cardInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
});
