# This file defines URL patterns for the accounts application, handling user registration, login, and management.

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),  # User registration 
    path('login/', views.login_view, name='login'),  # User login
    path('logout/', auth_views.LogoutView.as_view(
        next_page='home'  # Redirect to home after logout
    ), name='logout'),
    path('account/', views.account_dashboard, name='dashboard'),  # User account dashboard
    path('account/edit/', views.account_edit, name='edit'),  # Edit user account details
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',  # Template for password reset form
             email_template_name='accounts/password_reset_email.html',  # Email template for reset instructions
             success_url='/accounts/password-reset/done/'  # Redirect after successful reset request
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'  # Template for reset request confirmation
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',  # Template for password reset confirmation
             success_url='/accounts/password-reset-complete/'  # Redirect after successful password reset
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'  # Template for completion of password reset
         ),
         name='password_reset_complete'),
    
    # MFA URLs
    path('mfa/settings/', views.mfa_settings, name='mfa_settings'),  # Multi-factor authentication settings
    path('mfa/enable/', views.enable_mfa, name='enable_mfa'),  # Enable multi-factor authentication
    path('mfa/disable/', views.disable_mfa, name='disable_mfa'),  # Disable multi-factor authentication
    path('mfa/verify/', views.verify_mfa, name='verify_mfa'),  # Verify multi-factor authentication
    path('addresses/add/', views.add_address, name='add_address'),  # Add a new address
    path('addresses/', views.manage_addresses, name='manage_addresses'),  # Manage user addresses
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),  # Delete an address
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),  # Edit an existing address
]