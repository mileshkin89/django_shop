"""Stripe Checkout Session service layer."""

import logging

import stripe
from django.conf import settings

from .models import Order

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(order: Order, success_url: str, cancel_url: str) -> str:
    """Create a Stripe Checkout Session for the given order.

    Returns the Stripe-hosted URL the customer should be redirected to.
    """
    line_items = []
    for item in order.order_items.select_related("inventory", "product"):
        line_items.append({
            "price_data": {
                "currency": "usd",
                "unit_amount": int(item.inventory.price * 100),
                "product_data": {
                    "name": item.product.product_display_name,
                },
            },
            "quantity": item.quantity,
        })

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": str(order.id)},
    )

    order.stripe_session_id = session.id
    order.save(update_fields=["stripe_session_id", "updated_at"])

    return session.url


def handle_checkout_completed(session: dict) -> None:
    """Process a completed Stripe Checkout Session webhook event."""
    session_id = session["id"]

    try:
        order = Order.objects.get(stripe_session_id=session_id)
    except Order.DoesNotExist:
        logger.warning("Order not found for Stripe session %s", session_id)
        return

    if order.status != "Pending":
        logger.info(
            "Order %s already in status '%s', skipping", order.id, order.status,
        )
        return

    order.checkout_complete()
    logger.info("Order %s marked as Paid via Stripe webhook", order.id)
