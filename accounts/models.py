# This file defines the User, Address, and LoginAttempt models for the application, 
# including user roles and multi-factor authentication (MFA) functionality.

from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from functools import wraps
from django.http import HttpResponseForbidden
from django_otp.plugins.otp_totp.models import TOTPDevice

class User(AbstractUser):
    # User roles
    CUSTOMER = 'customer'
    ADMIN = 'admin'
    SUPERUSER = 'superuser'
    
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (ADMIN, 'Admin'),
        (SUPERUSER, 'Superuser'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CUSTOMER,
    )
    
    # Indicates if multi-factor authentication is enabled
    mfa_enabled = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Set user role and staff status based on superuser status
        if self.is_superuser:
            self.role = self.SUPERUSER
            self.is_staff = True
        elif self.role == self.ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False
        
        super().save(*args, **kwargs)
        
        # Update permissions only when role changes
        if self.role == self.ADMIN:
            self._set_admin_permissions()
        else:
            self.user_permissions.clear()

    def has_module_permission(self, request):
        # Check if the user is authenticated and has staff status
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff

    def _set_admin_permissions(self):
        # Assign admin-specific permissions to the user
        user_content_type = ContentType.objects.get_for_model(User)
        admin_permissions = [
            'view_user',
            'change_user',
            'view_customer',
            'change_customer',
        ]
        permissions = Permission.objects.filter(
            codename__in=admin_permissions,
            content_type=user_content_type
        )
        self.user_permissions.set(permissions)

    def is_admin_user(self):
        # Determine if the user has admin or superuser role
        return self.role in [self.ADMIN, self.SUPERUSER]

    def get_totp_device(self):
        # Retrieve the first confirmed TOTP device for the user
        devices = TOTPDevice.objects.filter(user=self, confirmed=True)
        return devices.first() if devices.exists() else None

    def enable_mfa(self):
        # Enable multi-factor authentication for the user
        self.mfa_enabled = True
        self.save()

    def disable_mfa(self):
        # Disable multi-factor authentication and remove TOTP devices
        self.mfa_enabled = False
        self.save()
        TOTPDevice.objects.filter(user=self).delete()

class Address(models.Model):
    # Link address to a user with a customer role
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.CUSTOMER})
    full_name = models.CharField(max_length=255)
    street_address1 = models.CharField(max_length=255)
    street_address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return a string representation of the address
        return f"{self.full_name}'s address in {self.city}"

    def get_complete_address(self):
        # Construct a complete address string, filtering out empty values
        address_parts = [
            self.street_address1,
            self.street_address2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))

class LoginAttempt(models.Model):
    # Record login attempts for users, including success status and IP address
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=255)  # Store username even if login fails
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)  # Whether attempt was on admin login

    class Meta:
        ordering = ['-timestamp']  # Order attempts by most recent
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'

    def __str__(self):
        # Return a string representation of the login attempt status
        status = "Success" if self.success else "Failed"
        return f"{status} - {self.username} at {self.timestamp}"
