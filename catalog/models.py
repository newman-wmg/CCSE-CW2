# This file defines the data models for the catalog, including categories and products.

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse

class MainCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/')
    
    class Meta:
        verbose_name_plural = "Categories"  # Plural name for the admin interface
        
    def __str__(self):
        return self.name  # String representation of the category
        
    def get_absolute_url(self):
        return reverse('catalog:category_products', args=[self.slug])  # URL for category products

class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Sub Categories"  # Plural name for the admin interface
        unique_together = ('main_category', 'slug')  # Ensure unique slug per main category
        
    def __str__(self):
        return f"{self.main_category.name} - {self.name}"  # String representation of the subcategory
        
    def get_absolute_url(self):
        return reverse('catalog:subcategory_products', args=[self.main_category.slug, self.slug])  # URL for subcategory products

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    subcategory = models.ForeignKey(SubCategory, related_name='products', on_delete=models.CASCADE)
    description = models.TextField()
    weight_and_measurements = models.TextField(
        help_text="Enter product dimensions and weight (e.g., Width: 80cm, Height: 120cm, Depth: 60cm, Weight: 25kg)",
        null=True,
        blank=True,
        verbose_name="Weight & Measurements"  # Label for the field
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])  # Price must be non-negative
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)  # Threshold for low stock warning
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False, help_text="Check to display this product on the homepage")  # Flag for featured products
    
    def __str__(self):
        return self.name  # String representation of the product
    
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold  # Check if stock is below the threshold
        
    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])  # URL for product detail

    class Meta:
        ordering = ['-created_at']  # Order products by creation date, newest first
