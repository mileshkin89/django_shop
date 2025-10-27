document.addEventListener('DOMContentLoaded', function() {
    const productPageContent = document.querySelector('.page-product');
    if (productPageContent) {
        // Accordion
        const accordionTitle = document.querySelector('.accordion-title');
        if (accordionTitle) {
            accordionTitle.addEventListener('click', function () {
                this.closest('.accordion-item').classList.toggle('active');
            });
        }
        // "Add to Cart" Button and Counter
        const cartControls = document.querySelector('.cart-controls');
        if (cartControls) {
            const addToCartBtn = cartControls.querySelector('#add-to-cart-btn');
            const quantityCounter = cartControls.querySelector('#quantity-counter');
            const decreaseBtn = quantityCounter.querySelector('[data-action="decrease"]');
            const increaseBtn = quantityCounter.querySelector('[data-action="increase"]');
            const quantityValueSpan = quantityCounter.querySelector('.quantity-value');
            let quantity = 0;
            let status = null;

            const slugElement = document.querySelector('[data-product-slug]');
            if (!slugElement) {
                console.error('Missing data-product-slug on page');
                return;
            }
            const slug = slugElement.dataset.productSlug;

            function updateView(qty) {
                if (qty === 0) {
                    addToCartBtn.classList.remove('is-hidden');
                    quantityCounter.classList.add('is-hidden');
                } else {
                    addToCartBtn.classList.add('is-hidden');
                    quantityCounter.classList.remove('is-hidden');
                    quantityValueSpan.textContent = `${qty} in cart`;
                }
            }

            function updateQuantity(qty) {
                fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ slug, quantity, status })
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
                        updateView(quantity);
                    } else {
                        console.error(data.error || 'Unknown error');
                    }
                })
                .catch(err => console.error('Error adding to cart:', err));
            }

            addToCartBtn.addEventListener('click', function () {
                quantity = 1;
                updateQuantity(quantity);
            });

            decreaseBtn.addEventListener('click', function () {
                if (quantity > 0) {
                    quantity--;
                    updateQuantity(quantity);
                }
            });

            increaseBtn.addEventListener('click', function () {
                quantity++;
                updateQuantity(quantity);
            });

            fetch(`/cart/add/?slug=${slug}&status=Cart`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                quantity = data.quantity || 0;
                status = data.status || null;
                updateView(quantity);
            })
            .catch(err => console.error('Error fetching initial quantity:', err));

            updateView(quantity);
        }
    }
})

