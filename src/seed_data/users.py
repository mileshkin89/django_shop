from django.db import transaction
from django.utils import timezone
from tqdm import tqdm
from faker import Faker

from django.contrib.auth import get_user_model
from seed_data.mixins import SaveInDBMixin


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

        self.user_model = User


    def seed_users(self):
        fake = Faker()
        users = []

        current_time = timezone.now()

        for i in tqdm(range(self.users_count)):
            user = self.user_model(
                username=fake.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True,
                is_staff=False,
                is_superuser=False,
                date_joined=current_time,
            )
            user.set_password(self.password)
            users.append(user)

            if i % self.batch_size == 0:
                self.bulk_insert(users, self.user_model)
                users = []

        if users:
            self.bulk_insert(users, self.user_model)


class UserCleaner:
    def __init__(self):
        self.user_model = User

    def cleen_users(self):
        count = 0

        non_admin_users = self.user_model.objects.exclude(username="admin")

        with transaction.atomic():
            if non_admin_users.exists():
                count, _ = non_admin_users.delete()

        return count




