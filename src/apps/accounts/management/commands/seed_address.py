import time

from django.core.management.base import BaseCommand

from apps.accounts.models import ShippingAddress
from seed_data.address.address import AddressGenerator


class Command(BaseCommand):
    help = 'Seeds the database with initial user delivery addresses.'

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=1000,
            help="How many users to create at once (default: 1000)",
        )


    def handle(self, *args, **options):
        batch_size = options["batch_size"]

        start = time.perf_counter()

        self.stdout.write(self.style.NOTICE(f"Starting to seed user delivery addresses..."))

        seed_data = AddressGenerator(
            batch_size=batch_size,
        )
        seed_data.seed_users()

        total = time.perf_counter() - start

        inserted_addresses = ShippingAddress.objects.count()

        self.stdout.write(self.style.SUCCESS(f"User delivery addresses seeded in {total:.3f}s"))
        self.stdout.write(self.style.SUCCESS(f"Total inserted {inserted_addresses} addresses."))
