document.addEventListener('DOMContentLoaded', function() {

    // --- Logic for Cart Page (cart.html) ---
    const cartPageContent = document.querySelector('.cart-page-wrapper');
    if (cartPageContent) {
        const cartItemsList = document.getElementById('cart-items-list');
        const cartTotalPriceElem = document.getElementById('cart-total-price');
        const slugElement = document.querySelector('[data-product-slug]');
        if (!slugElement) {
            console.error('Missing data-product-slug on page');
            return;
        }
        const slug = slugElement.dataset.productSlug;
        let quantity;

        function updateCartTotal() {
            let total = 0;
            document.querySelectorAll('.cart-item').forEach(item => {
                const priceText = item.querySelector('[data-item-total-price]').textContent;
                if (priceText) {
                    total += parseFloat(priceText.replace('$', ''));
                }
            });
            if (cartTotalPriceElem) cartTotalPriceElem.textContent = `$${total.toFixed(2)}`;
        }

        function updateQuantity(qty) {
            fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ slug, quantity })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Server returned ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    quantity = data.item_quantity;
                } else {
                    console.error(data.error || 'Unknown error');
                }
            })
            .catch(err => console.error('Error adding to cart:', err));
        }

        if (cartItemsList) {
            cartItemsList.addEventListener('click', function(event) {
                const cartItem = event.target.closest('.cart-item');
                if (!cartItem) return;
                const quantityElem = cartItem.querySelector('.quantity-value-cart');
                const itemTotalElem = cartItem.querySelector('[data-item-total-price]');
                const basePrice = parseFloat(cartItem.dataset.price);
                quantity = parseInt(quantityElem.textContent);
                if (event.target.closest('[data-action="increase"]')) {
                    quantity++;
                    updateQuantity(quantity);
                    updateCartTotal();
                } else if (event.target.closest('[data-action="decrease"]')) {
                    quantity = quantity > 1 ? quantity - 1 : 0;
                    updateQuantity(quantity);
                    updateCartTotal();
                }
                if (event.target.closest('[data-action="remove"]') || quantity === 0) {
                    cartItem.remove();
                } else {
                    quantityElem.textContent = quantity;
                    itemTotalElem.textContent = `$${(basePrice * quantity).toFixed(2)}`;
                }
            });
        }

        fetch(`/cart/add/?slug=${slug}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                quantity = data.quantity || 0;
            })
            .catch(err => console.error('Error fetching initial quantity:', err));

        updateCartTotal();
    }
})