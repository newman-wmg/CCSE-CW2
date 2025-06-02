# This file defines the Cart and CartItem models for managing user shopping carts and their contents.

from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One cart per user
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        # Calculate the total price of all items in the cart
        return sum(item.get_cost() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']  # Order items by the most recently added

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_cost(self):
        # Calculate the cost for this cart item based on product price and quantity
        return self.product.price * self.quantity