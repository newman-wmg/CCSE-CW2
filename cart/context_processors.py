# This file contains context processors for the cart functionality.

from .models import Cart

def cart_counter(request):
    # Check if the user is authenticated and not an admin
    if request.user.is_authenticated and not request.user.is_staff:
        # Retrieve or create a cart for the authenticated user
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Calculate the total item count in the cart
        item_count = sum(item.quantity for item in cart.items.all())
        return {'cart_item_count': item_count}
    # Return zero if the user is not authenticated or is an admin
    return {'cart_item_count': 0} 