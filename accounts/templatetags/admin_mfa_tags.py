# This file provides custom template filters for handling Multi-Factor Authentication (MFA) verification status.

from django import template
from django_otp.plugins.otp_totp.models import TOTPDevice

register = template.Library()

@register.filter
def has_verified_totp(user):
    # Check if the user is authenticated before verifying TOTP status.
    if not user.is_authenticated:
        return False
    # Determine if the user has a confirmed TOTP device, indicating successful MFA setup.
    return TOTPDevice.objects.filter(user=user, confirmed=True).exists() 