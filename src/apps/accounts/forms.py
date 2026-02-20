from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm as AuthPasswordResetForm,
    SetPasswordForm as AuthSetPasswordForm,
)
from django.core.exceptions import ValidationError
from django import forms

from .models import User


class PasswordResetRequestForm(AuthPasswordResetForm):
    """Form for requesting a password reset link by email (unauthenticated users)."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "Input", "placeholder": "Enter your email address", "autocomplete": "email"}
        ),
    )


class PasswordResetConfirmForm(AuthSetPasswordForm):
    """Form for setting new password from reset link (new_password1, new_password2)."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {"class": "Input", "placeholder": "Enter new password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "Input", "placeholder": "Repeat new password"}
        )


class PasswordChangeForm(forms.Form):
    """Form for authenticated user to change password."""

    current_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={"class": "Input", "placeholder": "Enter current password"}),
    )
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"class": "Input", "placeholder": "Enter new password"}),
        min_length=8,
    )
    new_password_confirm = forms.CharField(
        label="Repeat new password",
        widget=forms.PasswordInput(attrs={"class": "Input", "placeholder": "Repeat new password"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        value = self.cleaned_data.get("current_password")
        if value and not self.user.check_password(value):
            raise ValidationError("Current password is incorrect.")
        return value

    def clean_new_password_confirm(self):
        new_password = self.cleaned_data.get("new_password")
        new_password_confirm = self.cleaned_data.get("new_password_confirm")
        if new_password is not None and new_password_confirm is not None and new_password != new_password_confirm:
            raise ValidationError("The new passwords do not match.")
        return new_password_confirm

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password_confirm"])
        if commit:
            self.user.save(update_fields=["password"])
        return self.user


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

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)

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
                shipping_obj = user_instance.shipping_addresses.first()
                if shipping_obj:
                    self.fields['shipping_address'].initial = shipping_obj.shipping_address
            except Exception:
                pass