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

    def seed_inventories(self):
        inventories = []

        products = Product.objects.all().only("id")

        for product in tqdm(products.iterator(), total=Product.objects.count()):
            price = random.randint(200, 5000) / 100

            inventory = Inventory(
                product=product,
                stock=random.randint(0, 80),
                price=price,
            )

            if inventory.stock == 0:
                product.is_active = False
                product.save()

            inventories.append(inventory)

        #     if len(inventories) >= self.batch_size:
        #         self.bulk_insert(inventories, Inventory)
        #         inventories = []
        #
        # if inventories:
        #     self.bulk_insert(inventories, Inventory, self.batch_size)
        self._bulk_create(inventories, Inventory, self.batch_size)


class InventoryCleaner(DataCleanerMixin):
    def __init__(self):
        self.inventory = [
            ("inventory", Inventory.objects.all())
        ]

        self.desc = "Cleaning inventory"

    def clean_inventory(self):
        self.clean_data(self.inventory, self.desc)
