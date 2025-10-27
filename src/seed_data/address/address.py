import random
from tqdm import tqdm
from faker import Faker

from django.db import transaction
from django.contrib.auth import get_user_model

from apps.accounts.models import ShippingAddress
from seed_data.mixins import SaveInDBMixin


User = get_user_model()

class AddressGenerator(SaveInDBMixin):
    def __init__(
            self,
            batch_size: int = 1000,
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


class AddressCleaner:
    def __init__(self):
        self.addresses = [
            ("address", ShippingAddress.objects.all())
        ]

    def cleen_users(self):
        with transaction.atomic():
            for label, qs in tqdm(self.addresses, desc="Cleaning addresses"):
                count, _ = qs.delete()
                tqdm.write(f"Deleted {count} rows from {label}")






