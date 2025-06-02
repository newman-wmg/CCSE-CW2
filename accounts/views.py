# This file contains views for user account management, including registration, profile editing, and multi-factor authentication (MFA) settings.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import CustomUserCreationForm, UserEditForm
from django.contrib.auth import login, get_user_model
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.urls import reverse
import qrcode
import qrcode.image
from io import BytesIO
import base64
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from orders.models import Order
from .models import Address
from django import forms
from django.urls import reverse

User = get_user_model()

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            login(request, user)  # Log in the user after successful registration
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def account_dashboard(request):
    # Redirect admins to Django admin interface
    if request.user.is_staff:
        return redirect('admin:index')
    
    # Get recent orders for the user
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get address information for the user
    addresses = Address.objects.filter(user=request.user)
    address_count = addresses.count()
    
    return render(request, 'accounts/dashboard.html', {
        'user': request.user,
        'recent_orders': recent_orders,
        'has_addresses': address_count > 0,
        'address_count': address_count
    })

@login_required
def account_edit(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # Save the updated user information
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:dashboard')
    else:
        form = UserEditForm(instance=request.user)
    
    return render(request, 'accounts/edit.html', {
        'form': form
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == User.CUSTOMER:
                auth_login(request, user)  # Log in the customer
                return redirect('accounts:dashboard')
            else:
                form.add_error(None, "")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def mfa_settings(request):
    user = request.user
    totp_device = user.get_totp_device()  # Retrieve the user's TOTP device
    
    context = {
        'mfa_enabled': user.mfa_enabled,
        'totp_device': totp_device,
    }
    return render(request, 'accounts/mfa_settings.html', context)

@login_required
def enable_mfa(request):
    user = request.user
    
    if request.method == 'POST':
        token = request.POST.get('token')
        device = user.totpdevice_set.first()  # Get the user's TOTP device
        
        if device.verify_token(token):
            device.confirmed = True
            device.save()  # Confirm the device
            user.enable_mfa()  # Enable MFA for the user
            request.session['mfa_verified'] = True
            messages.success(request, 'MFA has been enabled successfully.')
            return redirect('accounts:mfa_settings')
        else:
            messages.error(request, 'Invalid token. Please try again.', extra_tags='danger')
    
    # Create new TOTP device if it doesn't exist
    device, created = TOTPDevice.objects.get_or_create(
        user=user, 
        confirmed=False,
        defaults={'name': 'Customer MFA Device'}
    )
    if created:
        device.save()
    
    # Generate QR code for MFA setup
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    provisioning_uri = device.config_url
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'qr_code': qr_code_base64,
        'secret_key': device.config_url,
    }
    return render(request, 'accounts/enable_mfa.html', context)

@login_required
def disable_mfa(request):
    if request.method == 'POST':
        user = request.user
        user.disable_mfa()  # Disable MFA for the user
        messages.success(request, 'MFA has been disabled.')
    return redirect('accounts:mfa_settings')

def verify_mfa(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        user = request.user
        device = user.get_totp_device()  # Retrieve the user's TOTP device
        
        if device and device.verify_token(token):
            request.session['mfa_verified'] = True
            return redirect(request.session.get('next', 'home'))
        else:
            messages.error(request, 'Invalid token. Please try again.', extra_tags='danger')
    
    return render(request, 'accounts/verify_mfa.html')

class AdminMFASetupView(UserPassesTestMixin, View):
    template_name = 'secret/mfa_setup.html'
    
    def test_func(self):
        return self.request.user.is_staff  # Ensure the user is an admin
    
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('admin:login')
            
        # Create or get TOTP device for admin
        device, created = TOTPDevice.objects.get_or_create(
            user=request.user,
            confirmed=False,
            defaults={'name': 'Admin MFA Device'}
        )
        
        # Generate QR code for admin MFA setup
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(device.config_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered)
        qr_code = base64.b64encode(buffered.getvalue()).decode()
        
        return render(request, self.template_name, {
            'qr_code': qr_code,
            'secret': device.config_url
        })
    
    def post(self, request):
        token = request.POST.get('token')
        device = TOTPDevice.objects.get(user=request.user, confirmed=False)
        
        if device.verify_token(token):
            device.confirmed = True
            device.save()  # Confirm the device for admin
            request.session['admin_mfa_verified'] = True
            messages.success(request, 'MFA has been enabled for your admin account')
            return redirect('admin:index')
        
        messages.error(request, 'Invalid token')
        return redirect('admin_mfa_setup')

class AdminMFAVerifyView(UserPassesTestMixin, View):
    template_name = 'secret/verify_mfa.html'
    
    def test_func(self):
        return self.request.user.is_staff  # Ensure the user is an admin
    
    def get(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('admin:login')
        
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        if not device:
            return redirect('admin_mfa_setup')
            
        return render(request, self.template_name)
    
    def post(self, request):
        token = request.POST.get('token')
        device = TOTPDevice.objects.get(user=request.user, confirmed=True)
        
        if device.verify_token(token):
            request.session['admin_mfa_verified'] = True
            next_url = request.session.get('admin_next', 'admin:index')
            return redirect(next_url)
        
        messages.error(request, 'Invalid token')
        return redirect('admin_mfa_verify')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name',
            'street_address1',
            'street_address2',
            'city',
            'state_province',
            'postal_code',
            'country',
            'phone_number',
            'delivery_instructions'
        ]

@login_required
def add_address(request):
    # Define safe redirect destinations
    allowed_redirects = {
        'dashboard': 'accounts:dashboard',
        'manage_addresses': 'accounts:manage_addresses',
    }

    # Get redirect key from user input, fallback to 'manage_addresses'
    next_param = request.GET.get('next', 'manage_addresses')
    next_url = allowed_redirects.get(next_param, 'accounts:manage_addresses')

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user # Associate the address with the logged-in user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect(next_url)
    else:
        form = AddressForm()

    return render(request, 'accounts/add_address.html', {
        'form': form,
        'next_url': next_url
    })

@login_required
def manage_addresses(request):
    addresses = Address.objects.filter(user=request.user)  # Retrieve addresses for the user
    return render(request, 'accounts/manage_addresses.html', {'addresses': addresses})

@login_required
def delete_address(request, address_id):
    if request.method == 'POST':
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()  # Delete the specified address
        messages.success(request, 'Address deleted successfully.')
    return redirect('accounts:manage_addresses')

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    # Define safe redirect destinations
    allowed_redirects = {
        'dashboard': 'accounts:dashboard',
        'manage_addresses': 'accounts:manage_addresses',
    }

    # Get redirect key from user input, fallback to 'manage_addresses'
    next_param = request.GET.get('next', 'manage_addresses')
    next_url = allowed_redirects.get(next_param, 'accounts:manage_addresses')

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()  # Save the updated address information
            messages.success(request, 'Address updated successfully.')
            return redirect(next_url)
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/add_address.html', {
        'form': form,
        'next_url': next_url,
        'is_edit': True # Indicate that this is an edit operation
    })