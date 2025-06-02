# This file handles the views related to the shopping cart functionality, including adding, removing, and updating items.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from catalog.models import Product

@login_required
def cart_detail(request):
    # Retrieve or create a cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)
    # Fetch all items in the cart with related product information
    cart_items = cart.items.select_related('product').all()
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'cart_items': cart_items})

@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('catalog:product_detail', pk=product_id)
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to add items to cart.')
        return redirect('accounts:login')
        
    if request.user.is_staff:  # Prevent admin users from adding items to the cart
        messages.error(request, 'Administrators cannot add items to cart.')
        return redirect('catalog:product_detail', pk=product_id)
            
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:  # Check if the product is in stock
        messages.error(request, 'Sorry, this product is out of stock.')
        return redirect('catalog:product_detail', pk=product_id)
        
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )
    if not created:  # If the item already exists, increase its quantity
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, item_id):
    # Remove the specified item from the user's cart
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')

@login_required
def update_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate the requested quantity against available stock
        if quantity > cart_item.product.stock:
            return JsonResponse({
                'status': 'error',
                'message': f'Only {cart_item.product.stock} items available in stock',
                'available_stock': cart_item.product.stock
            })
            
        if quantity > 0:  # Update quantity or delete item if quantity is zero
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def clear_cart(request):
    if request.method == 'POST':
        # Clear all items from the user's cart
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        messages.success(request, 'Cart cleared successfully.')
    return redirect('cart:cart_detail')
