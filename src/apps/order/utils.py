from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from typing import Optional
from .models import Order, OrderToken, OrderItem, Inventory
from django.contrib.auth import get_user_model

User = get_user_model()


def merge_guest_cart_to_user_cart(guest_order: Order, user: User) -> Optional[Order]:
    """
    Merge items from a guest cart into the authenticated user's cart.

    Args:
        guest_order: Guest cart (Order with token, without user)
        user: Authenticated user to receive merged items

    Returns:
        The user's cart after merge (or None if no guest cart provided)
    """
    if not guest_order:
        return None

    user_order = Order.get_or_create_for_user(user)

    if not guest_order.order_items.exists():
        return user_order

    with transaction.atomic():
        guest_items = list(guest_order.order_items.select_related('product', 'inventory').all())

        for guest_item in guest_items:
            product = guest_item.product
            guest_inventory = guest_item.inventory
            guest_quantity = guest_item.quantity

            guest_inventory.refresh_from_db()

            # Find matching item in the user's cart 
            user_item = user_order.order_items.select_related('inventory').filter(product=product).first()

            if user_item:
                # Sum quantities but cap by available stock
                user_inventory = user_item.inventory
                user_inventory.refresh_from_db()

                new_quantity = user_item.quantity + guest_quantity
                available_stock = user_inventory.stock
                new_quantity = min(new_quantity, available_stock)

                if new_quantity > 0:
                    user_item.quantity = new_quantity
                    user_item.save()
                else:
                    user_item.delete()
            else:
                # Add new item to user cart if in stock
                available_stock = guest_inventory.stock
                if available_stock > 0:
                    quantity_to_add = min(guest_quantity, available_stock)
                    OrderItem.objects.create(
                        order=user_order,
                        product=product,
                        inventory=guest_inventory,
                        quantity=quantity_to_add
                    )

        # Recalculate total price
        user_order.refresh_from_db()
        items_for_total = list(user_order.order_items.select_related('inventory').all())
        total_sum = sum(
            Decimal(str(item.quantity)) * Decimal(str(item.inventory.price))
            for item in items_for_total
        )
        user_order.total_price = total_sum.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        user_order.save(update_fields=["total_price", "updated_at"])

        # Clear guest cart after successful merge
        guest_order.order_items.all().delete()
        guest_order.total_price = 0
        guest_order.save(update_fields=["total_price", "updated_at"])

        return user_order


def get_guest_cart_from_token(token_value: Optional[str]) -> Optional[Order]:
    """
    Resolve a guest cart by token.

    Args:
        token_value: Token value from cookie

    Returns:
        Guest Order (with token, without user) or None
    """
    if not token_value:
        return None

    try:
        token = OrderToken.objects.filter(token=token_value).first()
        if token and not token.is_expired:
            guest_order = Order.get_or_create_for_token(token)

            # Ensure it is a guest cart (no user, matching token)
            if guest_order and guest_order.user is None and guest_order.token == token:
                return guest_order
    except Exception:
        return None

    return None

