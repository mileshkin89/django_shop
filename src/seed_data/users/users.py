from django.db import transaction
from django.utils import timezone
from tqdm import tqdm
from faker import Faker

from django.contrib.auth import get_user_model
from seed_data.mixins import SaveInDBMixin
from seed_data.users.utils import get_random_phone_number

User = get_user_model()

class UserGenerator(SaveInDBMixin):
    def __init__(
            self,
            users_count: int = 1000,
            batch_size: int = 500,
            password: str = "password123",
    ):
        super().__init__()
        self.users_count: int = users_count
        self.batch_size: int = batch_size
        self.password: str = password


    def seed_users(self):
        fake = Faker()
        users = []
        hash_password = None

        current_time = timezone.now()

        for i in tqdm(range(self.users_count)):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                phone_number=get_random_phone_number(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True,
                is_staff=False,
                is_superuser=False,
                date_joined=current_time,
            )
            if hash_password:
                user.password = hash_password
            else:
                user.set_password(self.password)
                hash_password = user.password
            users.append(user)

            if i % self.batch_size == 0:
                self.bulk_insert(users, User)
                users = []

        if users:
            self.bulk_insert(users, User)


class UserCleaner:
    def __init__(self):
        self.non_admin_users = [
            ("users", User.objects.exclude(username="admin"))
        ]

    def cleen_users(self):
        with transaction.atomic():
            for label, qs in tqdm(self.non_admin_users, desc="Cleaning users"):
                count, _ = qs.delete()
                tqdm.write(f"Deleted {count} rows from {label}")






