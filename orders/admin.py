# This file defines the admin interface for managing orders and their items.

from django.contrib import admin
from django.template.loader import render_to_string
from .models import Order, OrderItem
from .notifications import send_order_status_email

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding order items directly in the admin

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_shipping_address', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'user__email', 'user__username', 'shipping_address__full_name', 
                    'shipping_address__city', 'shipping_address__postal_code']
    readonly_fields = ['user', 'created_at', 'updated_at', 'total_amount', 'stripe_payment_intent', 
                      'shipping_address_details']
    inlines = [OrderItemInline]
    
    def get_shipping_address(self, obj):
        if obj.shipping_address:
            return f"{obj.shipping_address.full_name} - {obj.shipping_address.city}"
        return "No address"  # Provide a fallback if no address is available
    get_shipping_address.short_description = 'Shipping Address'

    def shipping_address_details(self, obj):
        if obj.shipping_address:
            context = {'address': obj.shipping_address}
            return render_to_string('secret/orders/shipping_address_detail.html', context)
        return "No address information available"  # Fallback for missing address details
    
    # Define actions for changing order status
    actions = ['mark_as_pending', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled']
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
        for order in queryset:
            send_order_status_email(order, 'pending')  # Notify user of status change
    mark_as_pending.short_description = "Mark selected orders as pending"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        if updated:
            for order in queryset:
                send_order_status_email(order, 'shipped')  # Notify user of status change
            self.message_user(request, f'{updated} orders marked as shipped and notifications sent')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        if updated:
            for order in queryset:
                send_order_status_email(order, 'delivered')  # Notify user of status change
            self.message_user(request, f'{updated} orders marked as delivered and notifications sent')
    mark_as_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status='canceled')
        if updated:
            for order in queryset:
                send_order_status_email(order, 'canceled')  # Notify user of status change
            self.message_user(request, f'{updated} orders marked as canceled and notifications sent')
    mark_as_canceled.short_description = "Mark selected orders as canceled"
    
    # Customize the change form
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total_amount', 'shipping_address_details')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section for date fields
        }),
        ('Payment Information', {
            'fields': ('stripe_payment_intent',),
            'classes': ('collapse',)  # Collapsible section for payment details
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Check if editing an existing order
            return self.readonly_fields
        return []

    def has_add_permission(self, request):
        return False  # Prevent adding orders manually

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff  # Allow deletion for staff only

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff  # Allow changes for staff only

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff  # Allow viewing for staff only

    def has_module_permission(self, request):
        return request.user.is_staff  # Allow access to the Orders module for staff only

    def save_model(self, request, obj, form, change):
        if change:
            old_status = Order.objects.get(pk=obj.pk).status
            super().save_model(request, obj, form, change)
            # Notify user if the order status has changed
            if old_status != obj.status:
                send_order_status_email(obj, obj.status)
        else:
            super().save_model(request, obj, form, change)
