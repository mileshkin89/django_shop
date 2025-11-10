from typing import Optional
from django.http import HttpRequest
from django.utils.crypto import get_random_string

from .models import Order, OrderToken

TOKEN_LENGTH = 32


class OrderResolver:

    @staticmethod
    def resolve(request: HttpRequest, order_token_value: Optional[str]) -> Order:
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return Order.get_or_create_for_user(user)

        if order_token_value is not None:
            token = OrderToken.objects.filter(token=order_token_value).first()

            if token:
                if token.is_expired:
                    order = Order.objects.filter(token=token).first()

                    new_value = get_random_string(TOKEN_LENGTH)
                    new_token = OrderToken.objects.create(token=new_value)

                    if order:
                        order.token = new_token
                        order.save(update_fields=["token", "updated_at"])
                    else:
                        order = Order.get_or_create_for_token(new_token)

                    setattr(request, "_order_token_to_delete", True)
                    setattr(request, "_order_token_to_set", new_value)

                    token.delete()
                    return order

                return Order.get_or_create_for_token(token)

        new_value = get_random_string(TOKEN_LENGTH)
        new_token = OrderToken.objects.create(token=new_value)
        order = Order.get_or_create_for_token(new_token)
        setattr(request, "_order_token_to_set", new_value)
        return order
