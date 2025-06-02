# This file defines the admin interface for managing User and LoginAttempt models,
# including custom permissions and fieldsets based on user roles.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from .models import User, LoginAttempt
from .forms import AdminUserForm

# Unregister the default Group model from the admin site as it's not used in this application.
admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = AdminUserForm
    
    # Display relevant user fields in the admin list view for better visibility.
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'first_name', 'last_name'),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        # Define fieldsets based on whether the user is creating a new user or editing an existing one.
        if not obj:
            return self.add_fieldsets
            
        if request.user.is_superuser:
            # Superusers have access to all fields.
            return (
                (None, {'fields': ('username', 'password')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
                ('Permissions', {
                    'fields': ('role', 'is_active', 'is_staff', 'is_superuser'),
                }),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )
        else:
            # Non-superusers have limited access to fields.
            return (
                (None, {'fields': ('username',)}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
                ('Status', {'fields': ('is_active',)}),
            )
    
    def get_queryset(self, request):
        # Filter the queryset based on the user's role to restrict access to certain users.
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(role=User.CUSTOMER)
        return qs
    
    def has_module_permission(self, request):
        # Check if the user is authenticated and has the necessary permissions to access the module.
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.ADMIN
    
    def has_view_permission(self, request, obj=None):
        # Allow viewing if the user is a superuser or has admin role.
        return request.user.is_superuser or request.user.role == User.ADMIN
    
    def has_change_permission(self, request, obj=None):
        # Allow changes if the user is a superuser or the object belongs to a customer.
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.role == User.CUSTOMER
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion if the user is a superuser or the object belongs to a customer.
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.role == User.CUSTOMER

    def save_model(self, request, obj, form, change):
        # Preserve original role and permissions for non-superusers when editing.
        if not request.user.is_superuser:
            if change:
                original_obj = self.model.objects.get(pk=obj.pk)
                obj.role = original_obj.role
                obj.is_staff = original_obj.is_staff
                obj.is_superuser = original_obj.is_superuser
        super().save_model(request, obj, form, change)

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    # Display relevant fields for login attempts to monitor user activity.
    list_display = ('timestamp', 'username', 'success', 'ip_address', 'is_admin')
    list_filter = ('success', 'is_admin', 'timestamp')
    search_fields = ('username', 'ip_address')
    readonly_fields = ('timestamp', 'username', 'ip_address', 'success', 'user', 'is_admin')
    
    def has_add_permission(self, request):
        # Prevent adding new login attempts directly through the admin interface.
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent changing existing login attempts.
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow deletion of login attempts only for superusers.
        return request.user.is_superuser

    def get_queryset(self, request):
        # Restrict access to login attempts for non-superusers.
        if not request.user.is_superuser:
            return self.model.objects.none()
        return super().get_queryset(request)
