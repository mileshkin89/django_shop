document.addEventListener('DOMContentLoaded', function() {

    // Function to update button state to "added" state
    function setButtonAsAdded(button) {
        button.disabled = true;
        const span = button.querySelector('span');
        if (span) {
            span.textContent = 'Added';
        }
        const icon = button.querySelector('i');
        if (icon) {
            if (icon.classList.contains('fa-cart-shopping')) {
                icon.classList.replace('fa-cart-shopping', 'fa-check');
            } else if (!icon.classList.contains('fa-check')) {
                icon.classList.add('fa-check');
            }
        }
        button.classList.add('is-added');
    }

    // Function to check if product is in cart
    function checkProductInCart(productItem) {
        const button = productItem.querySelector('.add-to-cart-btn-itemlist');
        if (!button) {
            return;
        }

        const slug = button.dataset.productSlug;
        if (!slug) {
            return;
        }

        fetch(`/cart/cart_item/?slug=${slug}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => {
            if (!res.ok) {
                throw new Error(`Server returned ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            // If quantity > 0, product is in cart
            if (data.quantity && data.quantity > 0) {
                setButtonAsAdded(button);
            }
        })
        .catch(err => {
            console.error('Error checking product in cart:', err);
        });
    }

    // Check all products on page load
    const productItems = document.querySelectorAll('.product-item');
    if (productItems.length > 0) {
        productItems.forEach(productItem => {
            checkProductInCart(productItem);
        });
    }

    // "Add to Cart" Button for product list
    const addToCartBtnItemlist = document.querySelectorAll('.add-to-cart-btn-itemlist');
    if (addToCartBtnItemlist) {
        addToCartBtnItemlist.forEach(button => {
            button.addEventListener('click', function () {
                const slug = this.dataset.productSlug;
                const quantity = 1;

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
                        console.log('Product added to cart:', data);
                        setButtonAsAdded(button);
                    } else {
                        console.error(data.error || 'Unknown error');
                    }
                })
                .catch(err => console.error('Error adding to cart:', err));
            });
        });
    }
})