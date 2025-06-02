# This file handles user login events, logging both successful and failed attempts for auditing purposes.

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from .models import LoginAttempt
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType

def get_client_ip(request):
    # Extracts the client's IP address from the request.
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_successful_login(sender, request, user, **kwargs):
    # Logs a successful login attempt, noting if it was an admin access.
    is_admin = request.path.startswith('/secret/')
    LoginAttempt.objects.create(
        user=user,
        username=user.username,
        ip_address=get_client_ip(request),
        success=True,
        is_admin=is_admin
    )

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    # Logs a failed login attempt, recording the username and IP address.
    is_admin = request.path.startswith('/secret/')
    LoginAttempt.objects.create(
        user=None,
        username=credentials.get('username', ''),
        ip_address=get_client_ip(request),
        success=False,
        is_admin=is_admin
    ) 