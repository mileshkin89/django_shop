document.addEventListener('DOMContentLoaded', function() {

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
                        button.disabled = true;
                        button.querySelector('span').textContent = 'Added';
                        button.querySelector('.fa-cart-shopping').classList.replace('fa-cart-shopping', 'fa-check');
                        button.classList.add('is-added');
                    } else {
                        console.error(data.error || 'Unknown error');
                    }
                })
                .catch(err => console.error('Error adding to cart:', err));
            });
        });
    }
})