# This file defines URL patterns for the catalog application.

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.category_list, name='category_list'),  # Main category listing view
    path('products/', views.ProductListView.as_view(), name='product_list'),  # List of all products
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='category_products'),  # Products filtered by category
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', 
         views.ProductListView.as_view(), name='subcategory_products'),  # Products filtered by subcategory
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),  # Detailed view of a single product
] 