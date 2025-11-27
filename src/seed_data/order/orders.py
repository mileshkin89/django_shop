import random
from typing import List
from tqdm import tqdm

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.order.models import Order, OrderItem
from seed_data.mixins import SaveInDBMixin, DataCleanerMixin


class OrderGenerator(SaveInDBMixin):
    def __init__(self, batch_size: int = 5000):
        super().__init__()
        self.batch_size = batch_size

    def seed_orders(self):
        users = list(User.objects.prefetch_related('shipping_address').all())

        products = list(Product.objects.select_related('inventory').filter(is_active=True))

        all_orders: List[Order] = []
        all_order_items: List[OrderItem] = []

        for user in tqdm(users, desc="Seeding Orders"):
            users_orders = random.randint(1,30)

            first_to_user = True
            for _ in range(users_orders):
                if first_to_user:
                    _status = random.choice(('Cart', 'Pending'))
                    first_to_user = False
                else:
                    _status = random.choice(('Paid', 'Shipped', 'Delivered', 'Completed'))

                order = Order(user=user, status=_status)
                shipping_address = user.shipping_address.first()
                if shipping_address:
                    order.shipping_address = shipping_address

                all_orders.append(order)

        self._bulk_create(all_orders, Order, batch_size=self.batch_size)

        orders = list(Order.objects.select_related('shipping_address').all())

        for order in tqdm(orders, desc="Seeding OrderItems"):
            order_total_price = 0
            items_in_order = random.randint(1, 5)
            for _ in range(items_in_order):
                product = random.choice(products)
                order_item = OrderItem(
                    order=order,
                    product=product,
                    inventory=product.inventory,
                    quantity=random.randint(1, 3)
                )
                all_order_items.append(order_item)

                order_total_price += product.inventory.price * order_item.quantity
            order.total_price = order_total_price

        self._bulk_create(all_order_items, OrderItem, batch_size=self.batch_size)
        self._bulk_update(orders, Order, fields=['total_price'], batch_size=self.batch_size)


class OrderCleaner(DataCleanerMixin):
    def __init__(self):
        self.orders = [
            ("orders", Order.objects.all())
        ]

        self.desc = "Cleaning orders"

    def clean_orders(self):
        self.clean_data(self.orders, self.desc)





