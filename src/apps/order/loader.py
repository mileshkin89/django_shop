from django.db.models import Prefetch, F

from .models import Order, OrderItem


ORDER_ITEM_SELECT_RELATED = (
    "product",
    "product__inventory",
)

ORDER_ITEM_ONLY_FIELDS = (
    "id",
    "quantity",
    "order__id",

    "product__id",
    "product__slug",
    "product__image_url",
    "product__product_display_name",
    "product__product_id",
    "product__year",

    "product__inventory__id",
    "product__inventory__stock",
    "product__inventory__reserved",
    "product__inventory__price",
)


class OrderLoader:
    @staticmethod
    def get_items_queryset():
        return (
            OrderItem.objects
            .select_related(*ORDER_ITEM_SELECT_RELATED)
            .only(*ORDER_ITEM_ONLY_FIELDS)
        )

    @classmethod
    def get_available_items_queryset(cls):
        return (
            cls.get_items_queryset()
            .filter(
                product__inventory__stock__gt=F("product__inventory__reserved"),
            )
        )

    @classmethod
    def get_order_queryset(cls, order_id: int):
        return (
            Order.objects
            .filter(pk=order_id)
            .select_related("user", "token")
            .prefetch_related(
                Prefetch(
                    'order_items',
                    queryset=cls.get_items_queryset(),
                    to_attr="items_list"
                ),
                Prefetch(
                    'order_items',
                    queryset=cls.get_available_items_queryset(),
                    to_attr="available_items_list"
                ),
            )
        )

    @classmethod
    def get_order(cls, order_id: int) -> Order:
        return cls.get_order_queryset(order_id).get()
