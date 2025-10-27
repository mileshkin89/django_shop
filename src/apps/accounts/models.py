from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r'^\+1\d{10}$',
    message="Please enter a valid phone number in the format +1XXXXXXXXXX (11 digits)"
)

class User(AbstractUser):
    username = models.CharField(
        max_length=50,
        unique=False,
        blank=True,
        null=True,
        verbose_name="username",
    )

    email = models.EmailField(
        max_length=50,
        unique=True,
        verbose_name="email address",
    )

    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        verbose_name="phone number",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='shipping_address',
    )

    shipping_address = models.TextField(default='Temporary address', null=True, blank=True)

    class Meta:
        ordering = ['shipping_address']