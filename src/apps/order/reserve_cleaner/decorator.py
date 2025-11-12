from functools import wraps
from apps.order.reserve_cleaner.cleaner import clean_expired


def clear_expired_reserves(view_func):
    """
    Decorator to clear expired order reserves before executing the view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        clean_expired()

        return view_func(request, *args, **kwargs)
    return _wrapped_view


# example of usage:
#
# from django.utils.decorators import method_decorator
# from apps.order.reserve_cleaner.decorator import clear_expired_reserves
#
# @method_decorator(clear_expired_reserves, name='dispatch')
# class ExampleView:
#   pass