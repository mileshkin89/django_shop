from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='shipping_address',
    )

    shipping_address = models.TextField()

    class Meta:
        ordering = ['shipping_address']