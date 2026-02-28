from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.order.cookies import OrderCookieManager
from apps.order.utils import get_guest_cart_from_token, merge_guest_cart_to_user_cart


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Merge the guest cart into the user's cart after social login."""

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)

        if not sociallogin.is_existing:
            return

        guest_token = OrderCookieManager.get_token(request)
        if not guest_token:
            return

        guest_order = get_guest_cart_from_token(guest_token)
        if guest_order:
            merge_guest_cart_to_user_cart(guest_order, sociallogin.user)
            request._order_token_to_delete = True
