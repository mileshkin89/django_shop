from django.http import HttpRequest
from apps.order.models import Order
from .models import Review


class PermissionMixin:
    """
    Provides helper permission checks for review and reply operations.
    """
    request: HttpRequest

    def _is_staff(self) -> bool:
        """
        Return True if the current user is a staff member.
        """
        return self.request.user.is_staff

    def _is_user_author(self) -> bool:
        """
        Return True if the current user is the author of the object returned by get_object().
        """
        return self.get_object().author == self.request.user

    def _is_user_author_or_staff(self) -> bool:
        """
        Return True if the current user is either the object's author or a staff member.
        """
        if self._is_staff():
            return True
        if self._is_user_author():
            return True
        return False

    def _is_author_product_buyer(self) -> bool:
        """
        Return True if the current user has previously purchased the product associated
        with the object (based on completed or active order statuses).
        """
        return Order.objects.filter(
            user=self.request.user,
            status__in=['Paid', 'Shipped', 'Delivered', 'Completed'],
            order_items__product=self.get_product(),
        ).exists()

    def _is_first_authors_comment(self) -> bool:
        """
        Return True if the current user has not yet created a review for the product
        returned by get_product().
        """
        return not Review.objects.filter(
            author=self.request.user,
            product=self.get_product(),
        ).exists()
