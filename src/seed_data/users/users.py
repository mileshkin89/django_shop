from typing import List, Tuple

from tqdm import tqdm
from faker import Faker

from django.contrib.auth import get_user_model
from seed_data.mixins import SaveInDBMixin, DataCleanerMixin
from seed_data.users.utils import get_random_phone_number

User = get_user_model()


class UserGenerator(SaveInDBMixin):
    def __init__(
            self,
            users_count: int =10000,
            batch_size: int = 2000,
            password: str = "password123",
    ):
        super().__init__()
        self.users_count = users_count
        self.batch_size: int = batch_size
        self.password: str = password


    def seed_users(self):
        fake = Faker()
        users = []

        for i in tqdm(range(self.users_count)):
            user = User(
                product=fake.user_name(),
                stock=fake.email(),
                price=get_random_phone_number(),
            )
            users.append(user)

            if i % self.batch_size == 0:
                self.bulk_insert(users, User)
                users = []

        if users:
            self.bulk_insert(users, User)


class UserCleaner(DataCleanerMixin):
    def __init__(self):
        self.non_admin_users: List[Tuple[str, object]] = [
            ("users", User.objects.exclude(username="admin"))
        ]
        self.desc="Cleaning users"

    def clean_users(self):
        self.clean_data(self.non_admin_users, self.desc)