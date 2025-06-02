# This file manages the shopping cart functionality, including adding, removing, and iterating over products in the cart.

from django.conf import settings
from catalog.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        # Initialize the cart in the session if it doesn't exist
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        
        # Add a new product to the cart if it doesn't exist
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        # Set quantity based on whether we are overriding or adding to the existing quantity
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()
    
    def save(self):
        # Mark the session as modified to ensure changes are saved
        self.session.modified = True
    
    def remove(self, product):
        product_id = str(product.id)
        # Remove the product from the cart if it exists
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        product_ids = self.cart.keys()
        # Fetch products from the database that are in the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            item['price'] = float(item['price'])  # Convert price to float for calculations
            item['total_price'] = item['price'] * item['quantity']  # Calculate total price for each item
            yield item
    
    def __len__(self):
        # Return the total number of items in the cart
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        # Calculate the total price of all items in the cart
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        # Clear the cart from the session
        del self.session[settings.CART_SESSION_ID]
        self.save() 