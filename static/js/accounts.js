
document.addEventListener('DOMContentLoaded', function() {
    // handles delete address confirmation
    const deleteButtons = document.querySelectorAll('.delete-address-btn');
    
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this address?')) {
                e.preventDefault(); // cancel form submission
            }
        });
    });
}); 