from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms

from .models import User


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'user@mail.com'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'})
    )

    
class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'user@mail.com'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'Input', 'placeholder': 'password'}),
        min_length=8
    )
    password_confirm = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput(attrs={'class': 'Input', 'placeholder': 'password'}),
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean_password_confirm(self):
        password = self.cleaned_data['password']
        password_confirm = self.cleaned_data['password_confirm']
        if password != password_confirm:
            raise ValidationError('The passwords do not match.')
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password_confirm'])
        if commit:
            user.save()
        return user


class UserAccountForm(forms.ModelForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'Input', 'placeholder': 'Value'})
    )
    first_name = forms.CharField(
        label="First name",
        widget=forms.TextInput(attrs={'class': 'Input', 'placeholder': 'Value'})
    )
    last_name = forms.CharField(
        label="Last name",
        widget=forms.TextInput(attrs={'class': 'Input', 'placeholder': 'Value'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'Input', 'placeholder': 'example@mail.com'})
    )
    phone_number = forms.CharField(
        label="Phone number",
        widget=forms.TextInput(attrs={'class': 'Input', 'placeholder': '+1XXXXXXXXXX'}),
        required=False
    )
    shipping_address = forms.CharField(
        label="Shipping address",
        widget=forms.Textarea(attrs={'class': 'Textarea', 'placeholder': 'Value', 'rows': '3'}),
        required=False
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'Input', 'placeholder': 'Value'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            user.phone_number = None

        if commit:
            user.save()

        shipping_text = self.cleaned_data.get('shipping_address')
        if shipping_text is not None:
            from .models import ShippingAddress
            shipping_obj = ShippingAddress.objects.filter(user=user).first()
            if shipping_obj is None:
                shipping_obj = ShippingAddress(user=user)
            shipping_obj.shipping_address = shipping_text or None
            if commit:
                shipping_obj.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_instance = self.instance if hasattr(self, 'instance') else None
        if user_instance and getattr(user_instance, 'pk', None):
            try:
                shipping_obj = user_instance.shipping_address.first()
                if shipping_obj:
                    self.fields['shipping_address'].initial = shipping_obj.shipping_address
            except Exception:
                pass