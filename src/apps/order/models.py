from django.core.exceptions import ValidationError
from django.db import models

from .choices import StatusChoices


class Order(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='order',
    )
    shipping_address = models.ForeignKey(
        'accounts.ShippingAddress',
        on_delete=models.RESTRICT,
        related_name='order',
    )

    status = models.CharField(max_length=15, choices=StatusChoices.choices)
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Ensure total_price is positive."""
        if self.total_price < 0:
            raise ValidationError({'total_price': 'Total price must be greater than 0.'})

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    class Meta:
        ordering = ['status', '-total_price', 'user__username', '-updated_at', '-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='order_item',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='order_item',
    )
    inventory = models.ForeignKey(
        'Inventory',
        on_delete=models.RESTRICT,
        related_name='order_item',
    )

    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price_items(self):
        return self.inventory.price * self.quantity

    def __str__(self):
        return f"{self.order.user.username} - {self.order.status}"

    class Meta:
        ordering = ['-inventory__price', '-quantity']


class Inventory(models.Model):
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.RESTRICT,
        related_name='inventory',
    )

    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Ensure total_price is positive."""
        if self.price < 0:
            raise ValidationError({'total_price': 'Total price must be greater than 0.'})

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_display_name} - {self.stock} ps - {self.price}$"

    class Meta:
        ordering = ['-stock', 'price', '-updated_at', '-created_at']


