document.addEventListener('DOMContentLoaded', function() {

    // --- Logic for Cart Page (cart.html) ---
    const cartPageContent = document.querySelector('.cart-page-wrapper');
    if (cartPageContent) {
        const cartItemsList = document.getElementById('cart-items-list');
        const cartTotalPriceElem = document.getElementById('cart-total-price');
        const cartSummaryElem = document.querySelector('.cart-summary'); 
        let quantity;

        function updateCartTotal(total) {
            if (cartTotalPriceElem) cartTotalPriceElem.textContent = `$${total.toFixed(2)}`;
        }

        function updateQuantity(slug, quantity) {
            fetch('/cart/cart_item/', {
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
                    if (data.order_id === null) {
                        cartItemsList.innerHTML = '<p class="cart-empty-message">Cart is empty</p>';
                        if (cartSummaryElem) {
                            cartSummaryElem.style.display = 'none';
                        }
                        updateCartTotal(0.00);
                    } else {
                        updateCartTotal(data.total_price);
                    }
                } else {
                    console.error(data.error || 'Unknown error');
                }
            })
            .catch(err => console.error('Error adding to cart:', err));
        }

        function fetchCartTotal() {
            fetch('/cart/total/', {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.total_price === 0.00) {
                        cartItemsList.innerHTML = '<p class="cart-empty-message">Cart is empty</p>';
                        if (cartSummaryElem) {
                            cartSummaryElem.style.display = 'none';
                        }
                        updateCartTotal(0.00); 
                    } else {
                        updateCartTotal(data.total_price);
                    }
                } else {
                    console.error(data.error || 'Unknown error');
                }
            })
            .catch(err => console.error('Error fetching cart total:', err));
        }

        function deleteItem(slug) {
            fetch('/cart/cart_item/', {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ slug })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Server returned ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    if (data.order_id === null) {
                        cartItemsList.innerHTML = '<p class="cart-empty-message">Cart is empty</p>';
                        if (cartSummaryElem) {
                            cartSummaryElem.style.display = 'none';
                        }
                        updateCartTotal(0.00);
                    } else {
                        updateCartTotal(data.total_price);
                    }
                } else {
                    console.error(data.error || 'Unknown error');
                }
            })
            .catch(err => console.error('Error deleted cart item:', err));
        }

        if (cartItemsList) {
            cartItemsList.addEventListener('click', function(event) {
                const cartItem = event.target.closest('.cart-item');
                if (!cartItem) return;
                const quantityElem = cartItem.querySelector('.quantity-value-cart');
                const itemTotalElem = cartItem.querySelector('[data-item-total-price]');
                const basePrice = parseFloat(cartItem.dataset.price);
                const itemSlug = cartItem.dataset.productSlug;
                quantity = parseInt(quantityElem.textContent);

                if (event.target.closest('[data-action="increase"]')) {
                    quantity++;
                    updateQuantity(itemSlug, quantity);
                } else if (event.target.closest('[data-action="decrease"]')) {
                    quantity = quantity > 1 ? quantity - 1 : 0;
                    if (quantity === 0) {
                        deleteItem(itemSlug);
                        cartItem.remove();
                    } else {
                        updateQuantity(itemSlug, quantity);
                    }
                }
                if (event.target.closest('[data-action="remove"]')) {
                    deleteItem(itemSlug);
                    cartItem.remove();
                } else {
                    quantityElem.textContent = quantity;
                    itemTotalElem.textContent = `$${(basePrice * quantity).toFixed(2)}`;
                }
            });
        }

        fetchCartTotal();
    }
})