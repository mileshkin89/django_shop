import random
from tqdm import tqdm

from apps.catalog.models import Product
from apps.order.models import Inventory
from seed_data.mixins import SaveInDBMixin, DataCleanerMixin


class InventoryGenerator(SaveInDBMixin):
    def __init__(
            self,
            batch_size: int = 5000,
    ):
        super().__init__()
        self.batch_size: int = batch_size

    def seed_users(self):
        inventory_s = []

        product_count = Product.objects.count()
        products = Product.objects.all()

        for i in tqdm(range(product_count)):
            product = products[i]
            price = random.randint(2, 50)
            for j in range(random.randint(1, 3)):
                inventory = Inventory(
                    product=product,
                    stock=random.randint(0, 80),
                    price=price + 0.99 * j,
                )
                inventory_s.append(inventory)

            if i % self.batch_size == 0:
                self.bulk_insert(inventory_s, Inventory)
                inventory_s = []

        if inventory_s:
            self.bulk_insert(inventory_s, Inventory)


class InventoryCleaner(DataCleanerMixin):
    def __init__(self):
        self.inventory = [
            ("inventory", Inventory.objects.all())
        ]

        self.desc = "Cleaning inventory"

    def clean_inventory(self):
        self.clean_data(self.inventory, self.desc)
