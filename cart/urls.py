# This file defines URL patterns for the shopping cart functionality.

from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),  # Displays the current contents of the cart.
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Adds a specified product to the cart.
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Removes an item from the cart by its ID.
    path('update/<int:item_id>/', views.update_quantity, name='update_quantity'),  # Updates the quantity of a specific item in the cart.
    path('clear/', views.clear_cart, name='clear_cart'),  # Empties the entire shopping cart.
]