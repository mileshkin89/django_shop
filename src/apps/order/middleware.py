from django.http import HttpRequest, HttpResponse

from .cookies import OrderCookieManager
from .loader import OrderLoader
from .resolver import OrderResolver


class OrderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        order_token_value = OrderCookieManager.get_token(request)
        order = OrderResolver.resolve(request, order_token_value)
        request.order = OrderLoader.get_order(order.pk)

        response = self.get_response(request)

        if getattr(request, "_order_token_to_delete", False):
            OrderCookieManager.clear_token(response)

        new_token = getattr(request, "_order_token_to_set", None)
        if new_token:
            OrderCookieManager.set_token(response, new_token)

        return response
