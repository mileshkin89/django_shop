from django.db import models


class StatusChoices(models.TextChoices):
    CART = 'Cart', 'Cart'
    PENDING = 'Pending', 'Pending'
    PAID = 'Paid', 'Paid'
    SHIPPED = 'Shipped', 'Shipped'
    DELIVERED = 'Delivered', 'Delivered'
    COMPLETED = 'Completed', 'Completed'