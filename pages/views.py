# This file handles the views for the pages in the application.
# It can be used to handle the home page, about page, contact page, etc.

from django.shortcuts import render
from catalog.models import Product, MainCategory

def home(request):
    featured_products = Product.objects.filter(featured=True)[:6]  # Show up to 6 featured products
    categories = MainCategory.objects.all()
    # Render the homepage with featured products and categories
    return render(request, 'pages/home.html', {
        'featured_products': featured_products,
        'categories': categories,
    })
