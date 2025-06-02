"""
URL configuration for securecart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pages.views import home
from accounts.views import AdminMFASetupView, AdminMFAVerifyView
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('', home, name='home'),
    # fake admin login page 
    path('admin/', include('admin_honeypot.urls')),
    # secret/ is the real admin page
    path('secret/mfa-setup/', AdminMFASetupView.as_view(), name='admin_mfa_setup'),
    path('secret/verify-mfa/', AdminMFAVerifyView.as_view(), name='admin_mfa_verify'),
    path('secret/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('catalog/', include('catalog.urls', namespace='catalog')),
    path('health/', health_check, name='health_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)