# This file defines the Order and OrderItem models for managing customer orders in the application.

from django.db import models
from django.conf import settings
from django.utils import timezone
from catalog.models import Product
from accounts.models import Address

class Order(models.Model):
    # Possible statuses for an order to track its progress
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    confirmation_email_sent = models.BooleanField(default=False) # Flag to indicate if a confirmation email has been sent

    def __str__(self):
        # String representation of the order
        return f"Order {self.id} - {self.user.username}"

    def can_cancel(self):
        # Check if the order can be canceled based on its status
        return self.status == 'pending'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        # String representation of the order item
        return f"{self.quantity}x {self.product.name} in Order {self.order.id}"
