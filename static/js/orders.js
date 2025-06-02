
document.addEventListener('DOMContentLoaded', function() {
    // handles cancel order confirmation
    const cancelButtons = document.querySelectorAll('.cancel-order-btn');
    
    cancelButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this order?')) {
                e.preventDefault(); // cancel form submission
            }
        });
    });
}); 