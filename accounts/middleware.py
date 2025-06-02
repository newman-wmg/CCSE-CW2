# This file implements middleware for managing Multi-Factor Authentication (MFA) 
# for users and admin staff, ensuring secure access to protected resources.

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django_otp.plugins.otp_totp.models import TOTPDevice

class MFAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user has MFA enabled and is authenticated
        if hasattr(request.user, 'mfa_enabled') and request.user.is_authenticated and request.user.mfa_enabled:
            # Paths that don't require MFA verification
            exempt_paths = [
                reverse('accounts:verify_mfa'),
                reverse('accounts:logout'),
                reverse('accounts:login'),
                reverse('accounts:register'),
                '/secret/',
                '/static/',
                '/media/',
            ]
            
            # Determine if the current path is exempt from MFA verification
            is_exempt = any(request.path.startswith(path) for path in exempt_paths)
            
            # Redirect to MFA verification if not exempt and MFA not verified
            if not is_exempt and not request.session.get('mfa_verified'):
                request.session['next'] = request.path
                return redirect('accounts:verify_mfa')
        
        response = self.get_response(request)
        return response 

class AdminMFAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Apply MFA checks only for staff accessing secret paths
        if request.path.startswith('/secret/') and request.user.is_staff:
            # Skip middleware for specific exempt paths
            exempt_paths = [
                '/secret/login/',
                '/secret/mfa-setup/',
                '/secret/verify-mfa/',
            ]
            if any(request.path.startswith(path) for path in exempt_paths):
                return self.get_response(request)
            
            # Verify if the user has a confirmed MFA device
            device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
            if device and not request.session.get('admin_mfa_verified'):
                request.session['admin_next'] = request.path
                return redirect('admin_mfa_verify')
            elif not device:
                return redirect('admin_mfa_setup')
                
        return self.get_response(request) 