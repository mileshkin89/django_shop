from django.conf import settings
from django.http import HttpRequest, HttpResponse


class OrderCookieManager:
    @staticmethod
    def get_token(request: HttpRequest) -> str | None:
        return request.COOKIES.get(settings.ORDER_COOKIE_NAME)

    @staticmethod
    def set_token(response: HttpResponse, token: str) -> None:
        response.set_cookie(
            key=settings.ORDER_COOKIE_NAME,
            value=token,
            max_age=settings.ORDER_COOKIE_AGE,
            secure=settings.ORDER_COOKIE_SECURE,
            httponly=settings.ORDER_COOKIE_HTTPONLY,
            samesite=settings.ORDER_COOKIE_SAMESITE
        )

    @staticmethod
    def clear_token(response: HttpResponse) -> None:
        response.delete_cookie(
            key=settings.ORDER_COOKIE_NAME,
            samesite=settings.ORDER_COOKIE_SAMESITE
        )
