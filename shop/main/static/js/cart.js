const minusBtn = document.querySelector('.minus');
const plusBtn = document.querySelector('.plus');

const qtySpan = document.querySelector('.qty-value');
const totalSpan = document.querySelector('.total');
const deleteBtn = document.querySelector('.delete-btn');

let price = 1500;
let quantity = 1;

function updateCart() {
    totalSpan.textContent = price * quantity;
    document.getElementById("cart-total").textContent = price * quantity;
}

plusBtn.addEventListener('click', () => {
    quantity++;
    qtySpan.textContent = quantity;
    updateCart();
});

minusBtn.addEventListener('click', () => {
    if (quantity > 1) {
        quantity--;
        qtySpan.textContent = quantity;
        updateCart();
    }
});

deleteBtn.addEventListener('click', () => {
    document.querySelector('.cart-item').remove();
    document.getElementById("cart-total").textContent = 0;
});