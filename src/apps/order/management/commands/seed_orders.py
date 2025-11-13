import time

from django.core.management.base import BaseCommand

from apps.order.models import Order
from seed_data.order.orders import OrderGenerator


class Command(BaseCommand):
    help = 'Seeds the database with initial users orders.'

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=5000,
            help="How many orders to create at once (default: 5000)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]

        start = time.perf_counter()

        self.stdout.write(self.style.NOTICE(f"Starting to seed orders..."))

        seed_data = OrderGenerator(
            batch_size=batch_size,
        )
        seed_data.seed_orders()

        total = time.perf_counter() - start

        inserted_rows = Order.objects.count()

        self.stdout.write(self.style.SUCCESS(f"Orders seeded in {total:.3f}s"))
        self.stdout.write(self.style.SUCCESS(f"Total inserted {inserted_rows} rows."))
