# This file defines the admin interface for managing categories and products in the application.

from django.contrib import admin
from django.utils.html import format_html
from .models import MainCategory, SubCategory, Product
from accounts.models import User
from django.db import models

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    prepopulated_fields = {'slug': ('name',)}  # Automatically generate slug from name
    extra = 1  # Number of empty forms to display

    def has_view_permission(self, request, obj=None):
        # Allow view permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_add_permission(self, request, obj=None):
        # Allow add permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_change_permission(self, request, obj=None):
        # Allow change permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_delete_permission(self, request, obj=None):
        # Allow delete permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN

class LowStockFilter(admin.SimpleListFilter):
    title = 'stock status'  # Display title for the filter
    parameter_name = 'low_stock'  # Query parameter name

    def lookups(self, request, model_admin):
        # Define options for the low stock filter
        return (
            ('yes', 'Low Stock'),
            ('no', 'Normal Stock'),
        )

    def queryset(self, request, queryset):
        # Filter queryset based on stock status
        if self.value() == 'yes':
            return queryset.filter(stock__lte=models.F('low_stock_threshold'))
        if self.value() == 'no':
            return queryset.filter(stock__gt=models.F('low_stock_threshold'))

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_image', 'subcategory_count')  # Columns to display in the list view
    prepopulated_fields = {'slug': ('name',)}  # Automatically generate slug from name
    inlines = [SubCategoryInline]  # Inline editing for subcategories
    search_fields = ('name', 'subcategories__name')  # Fields to search in the admin

    def subcategory_count(self, obj):
        # Return the count of subcategories for the main category
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategories'
    
    def display_image(self, obj):
        # Display the category image in the admin interface
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Category Image'
    
    def has_module_permission(self, request):
        # Check if the user has permission to access this admin module
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
    
    def has_view_permission(self, request, obj=None):
        # Allow view permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_add_permission(self, request):
        # Allow add permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_change_permission(self, request, obj=None):
        # Allow change permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_delete_permission(self, request, obj=None):
        # Allow delete permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'price', 'stock', 'is_low_stock', 'featured', 'display_image')  # Columns to display
    list_filter = (
        'subcategory__main_category',  # Filter by main category
        'subcategory',  # Filter by subcategory
        'created_at',  # Filter by creation date
        'featured',  # Filter by featured status
        LowStockFilter,  # Custom low stock filter
    )
    list_editable = ('featured',)  # Fields that can be edited directly in the list view
    search_fields = ('name', 'description')  # Fields to search in the admin
    prepopulated_fields = {'slug': ('name',)}  # Automatically generate slug from name
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'subcategory', 'price', 'image', 'featured')
        }),
        ('Product Details', {
            'fields': ('description', 'weight_and_measurements')
        }),
        ('Stock Information', {
            'fields': ('stock', 'low_stock_threshold')
        }),
    )
    
    def display_image(self, obj):
        # Display the product image in the admin interface
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Product Image'
    
    def is_low_stock(self, obj):
        # Check if the product is low in stock
        return obj.is_low_stock()
    is_low_stock.boolean = True  # Display as a boolean in the admin
    is_low_stock.short_description = 'Low Stock'
    
    def has_module_permission(self, request):
        # Check if the user has permission to access this admin module
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
    
    def has_view_permission(self, request, obj=None):
        # Allow view permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_add_permission(self, request):
        # Allow add permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_change_permission(self, request, obj=None):
        # Allow change permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
        
    def has_delete_permission(self, request, obj=None):
        # Allow delete permission for authenticated users with appropriate roles
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Customize the queryset for the subcategory foreign key field
        if db_field.name == "subcategory":
            kwargs["queryset"] = SubCategory.objects.all().select_related('main_category')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        # Filter the queryset based on low stock status if specified
        queryset = super().get_queryset(request)
        if request.GET.get('low_stock') == 'yes':
            return queryset.filter(stock__lte=models.F('low_stock_threshold'))
        elif request.GET.get('low_stock') == 'no':
            return queryset.filter(stock__gt=models.F('low_stock_threshold'))
        return queryset

    def changelist_view(self, request, extra_context=None):
        # Add low stock filter value to the context for the changelist view
        if not extra_context:
            extra_context = {}
        extra_context['low_stock_filter'] = request.GET.get('low_stock', '')
        return super().changelist_view(request, extra_context)