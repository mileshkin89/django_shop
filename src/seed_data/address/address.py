import random
from typing import Tuple, List
from tqdm import tqdm
from faker import Faker

from django.contrib.auth import get_user_model

from apps.accounts.models import ShippingAddress
from seed_data.mixins import SaveInDBMixin, DataCleanerMixin

User = get_user_model()


class AddressGenerator(SaveInDBMixin):
    def __init__(
            self,
            batch_size: int = 5000,
    ):
        super().__init__()
        self.batch_size: int = batch_size

    def seed_addresses(self):
        fake = Faker()
        addresses = []

        users = User.objects.all().only("id")

        for user in tqdm(users.iterator(), total=User.objects.count()):
            for j in range(random.randint(0, 3)):
                address = ShippingAddress(
                    user=user,
                    shipping_address=fake.address(),
                )
                addresses.append(address)

            if len(addresses) >= self.batch_size:
                self.bulk_insert(addresses, ShippingAddress)
                addresses = []

        if addresses:
            self.bulk_insert(addresses, ShippingAddress)


class AddressCleaner(DataCleanerMixin):
    def __init__(self):
        self.addresses: List[Tuple[str, object]] = [
            ("address", ShippingAddress.objects.all())
        ]
        self.desc = "Cleaning addresses"

    def clean_address(self):
        self.clean_data(self.addresses, self.desc)
