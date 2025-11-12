from django.utils import timezone

from ..models import Order


def clean_expired() -> None:
    """
    Clean up expired pending orders.

    Any exceptions raised during the cancellation process are caught and silently ignored.

    Returns:
        None
    """
    expired_orders = Order.objects.filter(
        status='Pending',
        reserve_expires_at__lt=timezone.now()
    )

    if expired_orders.exists():
        for order in expired_orders:
            try:
                order.checkout_cancel()
            except Exception:
                pass