from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from core import settings
from .choices import StatusChoices
from apps.accounts.models import User

TOKEN_LENGTH = 32


def default_order_token_expiry():
    return timezone.now() + settings.ORDER_TOKEN_LIFETIME


def set_reserve_token_expiry():
    return timezone.now() + settings.RESERVE_TOKEN_LIFETIME


class OrderToken(models.Model):
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Unique token used to identify anonymous carts via cookie."
    )
    expires_at = models.DateTimeField(
        default=default_order_token_expiry,
        help_text="Token expiration; anonymous carts past this date may be culled."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"OrderToken({self.token})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


class Order(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='user_orders',
        null=True,
        blank=True,
    )
    token = models.ForeignKey(
        OrderToken,
        on_delete=models.CASCADE,
        related_name='token_orders',
        null=True,
        blank=True,
    )
    shipping_address = models.ForeignKey(
        'accounts.ShippingAddress',
        on_delete=models.RESTRICT,
        related_name='shipping_orders',
        null=True,
        blank=True,
    )

    status = models.CharField(default='Cart', max_length=15, choices=StatusChoices.choices)
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    reserve_token = models.CharField(max_length=64, unique=True, db_index=True, null=True, blank=True)
    reserve_expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-total_price', '-updated_at', '-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                        (models.Q(user__isnull=False) & models.Q(token__isnull=True)) |
                        (models.Q(user__isnull=True) & models.Q(token__isnull=False))
                ),
                name='order_exactly_one_owner'
            ),
            models.UniqueConstraint(
                fields=['user', 'status'],
                condition=models.Q(user__isnull=False, status='Cart'),
                name='unique_cart_order_per_user'
            ),
            models.UniqueConstraint(
                fields=['token', 'status'],
                condition=models.Q(token__isnull=False, status='Cart'),
                name='unique_cart_order_per_token'
            ),
            models.CheckConstraint(
                check=(
                        (models.Q(status='Cart')) |
                        (models.Q(status__in=['Pending', 'Paid', 'Shipped', 'Delivered', 'Completed']) & models.Q(
                            user__isnull=False))
                ),
                name='only_authenticated_can_have_non_cart_status'
            ),
        ]

    @property
    def is_empty(self) -> bool:
        return not self.order_items.exists()

    @property
    def is_expired_reserve(self) -> bool:
        return timezone.now() >= self.reserve_expires_at

    # flow 'Cart' to 'Pending' state
    def start_checkout(self):
        self.status = 'Pending'
        self.reserve_token = get_random_string(TOKEN_LENGTH)
        self.reserve_expires_at = set_reserve_token_expiry()

        for item in self.order_items.select_related('inventory'):
            item.inventory.reserve(item.quantity)

        self.save(update_fields=['status', 'reserve_token', 'reserve_expires_at', 'updated_at'])

    # flow 'Pending' to 'Paid' state
    def checkout_complete(self):
        self.status = 'Paid'
        self.reserve_token = None
        self.reserve_expires_at = None

        for item in self.order_items.select_related('inventory'):
            item.inventory.release_to_paid(item.quantity)

        self.save(update_fields=['status', 'reserve_token', 'reserve_expires_at'])

    # flow 'Pending' to 'Cart' state
    def checkout_cancel(self):
        self.status = 'Cart'
        self.reserve_token = None
        self.reserve_expires_at = None

        for item in self.order_items.select_related('inventory'):
            item.inventory.release_to_cart(item.quantity)

        self.save(update_fields=['status', 'reserve_token', 'reserve_expires_at'])

    @classmethod
    def get_or_create_for_user(cls, user: User):
        order, _ = cls.objects.get_or_create(user=user, status='Cart')
        return order

    @classmethod
    def get_or_create_for_token(cls, token: OrderToken):
        order, _ = cls.objects.get_or_create(token=token, status='Cart')
        return order

    def clean(self):
        """Ensure total_price is positive."""
        if self.total_price < 0:
            raise ValidationError({'total_price': 'Total price must be greater than 0.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='order_items',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='product_order_items',
    )
    inventory = models.ForeignKey(
        'Inventory',
        on_delete=models.RESTRICT,
        related_name='inventory_order_items',
    )

    quantity = models.PositiveIntegerField(default=1)

    @property
    def get_total_price_items(self):
        return self.inventory.price * self.quantity

    def __str__(self):
        return f"{self.order.user.username} - {self.order.status}"

    class Meta:
        ordering = ['-inventory__price', '-quantity']


class Inventory(models.Model):
    product = models.OneToOneField(
        'catalog.Product',
        on_delete=models.RESTRICT,
        related_name='inventory',
    )

    stock = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # flow 'Cart' to 'Pending' state
    def reserve(self, quantity: int):
        if self.stock < quantity:
            raise ValidationError("Not enough stock.")
        self.stock -= quantity
        self.reserved += quantity
        self.save(update_fields=['reserved', 'stock', 'updated_at'])

    # flow 'Pending' to 'Paid' state
    def release_to_paid(self, quantity: int):
        self.reserved = max(self.reserved - quantity, 0)
        self.save(update_fields=['reserved', 'updated_at'])

    # flow 'Pending' to 'Cart' state
    def release_to_cart(self, quantity: int):
        self.reserved = max(self.reserved - quantity, 0)
        self.stock += quantity
        self.save(update_fields=['reserved', 'stock', 'updated_at'])

    def clean(self):
        """Ensure total_price is positive."""
        if self.price < 0:
            raise ValidationError({'total_price': 'Total price must be greater than 0.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_display_name} - {self.stock} ps - {self.price}$"

    class Meta:
        ordering = ['-stock', 'price', '-updated_at', '-created_at']
