import time

from django.core.management.base import BaseCommand
from seed_data.users import UserGenerator


class Command(BaseCommand):
    help = 'Seeds the database with initial user data.'

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=1000,
            help="Total number of users to generate (default: 1000)",
        )
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=500,
            help="How many users to create at once (default: 500)",
        )
        parser.add_argument(
            "--password",
            dest="password",
            type=str,
            default="password123",
            help="Password for all generated users (default: password123)",
        )

    def handle(self, *args, **options):
        users_count = options["count"]
        batch_size = options["batch_size"]
        password = options["password"]

        start = time.perf_counter()

        self.stdout.write(self.style.NOTICE(f"Starting to seed {users_count} users..."))

        seed_data = UserGenerator(
            users_count=users_count,
            batch_size=batch_size,
            password=password,
        )
        seed_data.seed_users()

        total = time.perf_counter() - start

        self.stdout.write(self.style.SUCCESS(f"Users seeded in {total:.3f}s"))
        self.stdout.write(self.style.SUCCESS(f"Total inserted {users_count} users."))
