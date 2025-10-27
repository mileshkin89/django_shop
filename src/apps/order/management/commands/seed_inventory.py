import time

from django.core.management.base import BaseCommand

from apps.order.models import Inventory
from seed_data.order.inventory import InventoryGenerator


class Command(BaseCommand):
    help = 'Seeds the database with initial user data.'

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=5000,
            help="How many users to create at once (default: 1000)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]

        start = time.perf_counter()

        self.stdout.write(self.style.NOTICE(f"Starting to seed inventory..."))

        seed_data = InventoryGenerator(
            batch_size=batch_size,
        )
        seed_data.seed_users()

        total = time.perf_counter() - start

        inserted_rows = Inventory.objects.count()

        self.stdout.write(self.style.SUCCESS(f"Users seeded in {total:.3f}s"))
        self.stdout.write(self.style.SUCCESS(f"Total inserted {inserted_rows} rows inventory."))
