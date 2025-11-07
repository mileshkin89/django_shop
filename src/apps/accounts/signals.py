from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.accounts.models import ShippingAddress

User = get_user_model()

@receiver(post_save, sender=User)
def create_shipping_address_for_new_user(sender, instance, created, **kwargs):
    if created:
        ShippingAddress.objects.create(user=instance, shipping_address="Default Shipping Address")
