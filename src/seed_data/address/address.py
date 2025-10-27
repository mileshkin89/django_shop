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
            batch_size: int = 2000,
    ):
        super().__init__()
        self.batch_size: int = batch_size

    def seed_users(self):
        fake = Faker()
        addresses = []

        users_count = User.objects.count()
        users = User.objects.all()

        for i in tqdm(range(users_count)):
            user = users[i]
            for j in range(random.randint(0, 3)):
                address = ShippingAddress(
                    user=user,
                    shipping_address=fake.address(),
                )
                addresses.append(address)

            if i % self.batch_size == 0:
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
