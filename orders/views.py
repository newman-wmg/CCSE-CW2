# This file contains the views for processing orders, including checkout, order creation, and order management.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from catalog.models import Product
from accounts.models import Address, User
import stripe
from .notifications import send_order_status_email
import decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('product').all()
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    # Set session expiry to 30 minutes (1800 seconds)
    request.session.set_expiry(1800)
    
    # Mark the session as modified
    request.session.modified = True

    # Retrieve user's addresses for shipping
    addresses = Address.objects.filter(user=request.user)
    if not addresses.exists():
        messages.warning(request, 'Please complete your profile by adding a shipping address before checkout.')
        return redirect('accounts:manage_addresses')

    # If this is not a POST request, always show the address selection page
    if request.method != 'POST':
        return render(request, 'orders/select_address.html', {
            'addresses': addresses,
            'cart': cart,
            'cart_items': cart_items
        })

    # Get selected address from POST data
    selected_address_id = request.POST.get('address_id')
    if not selected_address_id:
        messages.error(request, 'Please select a shipping address.')
        return render(request, 'orders/select_address.html', {
            'addresses': addresses,
            'cart': cart,
            'cart_items': cart_items
        })

    try:
        selected_address = addresses.get(id=selected_address_id)
    except Address.DoesNotExist:
        messages.error(request, 'Invalid address selected.')
        return render(request, 'orders/select_address.html', {
            'addresses': addresses,
            'cart': cart,
            'cart_items': cart_items
        })

    # Validate stock levels before proceeding to payment
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'Sorry, only {item.product.stock} units of {item.product.name} are available.')
            return redirect('cart:cart_detail')

    try:
        # Prepare line items for Stripe Checkout Session
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': int(item.product.price * 100),  # Convert price to pence
                    'product_data': {
                        'name': item.product.name,
                        'description': f'Quantity: {item.quantity}',
                    },
                },
                'quantity': item.quantity,
            })

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            customer_email=request.user.email,  # Pre-fill customer email to session
            success_url=request.build_absolute_uri(
                reverse('orders:create_order') + '?session_id={CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri(reverse('cart:cart_detail')),
        )

        # Store cart and address data in session AFTER creating checkout session
        request.session['pending_order'] = {
            'items': [{
                'product_id': item.product.id,
                'quantity': item.quantity,
                'price': str(item.product.price)
            } for item in cart_items],
            'total_amount': str(cart.get_total_price()),
            'shipping_address_id': selected_address.id,
            'stripe_session_id': checkout_session.id
        }
        
        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f'Error creating checkout session: {str(e)}')
        return redirect('cart:cart_detail')

@login_required
def create_order(request):
    """Create order after successful payment"""
    pending_order = request.session.get('pending_order')
    if not pending_order:
        messages.error(request, 'No pending order found.')
        return redirect('cart:cart_detail')

    # Retrieve the Stripe session and payment intent for verification
    try:
        stripe_session = stripe.checkout.Session.retrieve(pending_order['stripe_session_id'])
        payment_intent = stripe_session.payment_intent
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment verification failed: {str(e)}')
        return redirect('cart:cart_detail')

    cart = get_object_or_404(Cart, user=request.user)
    shipping_address = get_object_or_404(Address, id=pending_order['shipping_address_id'], user=request.user)

    try:
        with transaction.atomic():
            # Create order with shipping address and payment intent
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_amount=decimal.Decimal(pending_order['total_amount']),
                stripe_payment_intent=payment_intent
            )
            
            # Create order items and update stock accordingly
            for item_data in pending_order['items']:
                product = get_object_or_404(Product, id=item_data['product_id'])
                quantity = item_data['quantity']
                
                if quantity > product.stock:
                    raise ValueError(f'Insufficient stock for {product.name}')
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=decimal.Decimal(item_data['price'])
                )
                
                product.stock -= quantity  # Deduct quantity from stock
                product.save()

            cart.items.all().delete()  # Clear the cart after order creation
            del request.session['pending_order']  # Remove pending order from session

            return redirect('orders:confirmation', order_id=order.id)

    except Exception as e:
        messages.error(request, f'Error creating order: {str(e)}')
        return redirect('cart:cart_detail')

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Send confirmation email only if it hasn't been sent yet
    if not order.confirmation_email_sent:
        order.status = 'pending'
        send_order_status_email(order, 'pending')
        order.confirmation_email_sent = True
        order.save()
    
    return render(request, 'orders/confirmation.html', {'order': order})

@login_required
def order_list(request):
    # Retrieve and display the user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Get the referrer from query parameter or default to order list
    came_from = request.GET.get('from', 'orders')
    return render(request, 'orders/detail.html', {
        'order': order,
        'came_from': came_from
    })

@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.can_cancel():
        with transaction.atomic():
            # Restore stock levels for canceled order items
            for item in order.items.all():
                if item.product:  # Check if product still exists
                    item.product.stock += item.quantity
                    item.product.save()
            
            order.status = 'canceled'  # Update order status
            order.save()
            
            # Send cancellation email
            send_order_status_email(order, 'canceled')
            
            messages.success(request, 'Order has been canceled successfully.')
    else:
        messages.error(request, 'This order cannot be canceled.')
    return redirect('orders:detail', order_id=order.id)
