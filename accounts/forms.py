# This file contains forms for user and address management, including custom user creation and editing forms.

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Address

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required at the form level
        for field in self.fields.values():
            field.required = True

class UserEditForm(UserChangeForm):
    password = None # Exclude password field as it should be updated through a separate view
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required at the form level
        for field in self.fields.values():
            field.required = True

class AdminUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required at the form level
        for field in self.fields.values():
            field.required = True
            
        # Limit role choices to exclude superuser unless the user is a superuser
        if not kwargs.get('instance') or not kwargs['instance'].is_superuser:
            self.fields['role'].choices = [
                choice for choice in User.ROLE_CHOICES 
                if choice[0] != User.SUPERUSER
            ]

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
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address1': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }