
// gets CSRF token from the meta tag
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content;
}

document.addEventListener('DOMContentLoaded', function() {
    // Update the quantity of items in the cart
    document.querySelectorAll('.update-quantity-form input').forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            const itemId = form.dataset.itemId;
            const quantity = this.value;
            
            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRFToken()
                },
                body: `quantity=${quantity}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else if (data.status === 'error') {
                    alert(data.message);
                    // Reset the input to the available stock amount
                    if (data.available_stock) {
                        this.value = data.available_stock;
                    }
                }
            });
        });
    });
}); 