import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import ShippingAddress
from seed_data.address.address import AddressCleaner

User = get_user_model()

class Command(BaseCommand):
    help = "Clear user delivery addresses."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            dest="yes",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        address = ShippingAddress.objects.all()
        count = address.count()

        self.stdout.write(
            self.style.NOTICE(
                f"{count:,} addresses will be deleted"
            )
        )

        if count == 0:
            self.stdout.write(self.style.WARNING("No addresses to delete."))
            return

        confirmed = options["yes"]
        if not confirmed:
            answer = input(
                f"This will DELETE {count:,} addresses. "
                "Are you sure? Type 'yes' to continue: "
            )
            if answer.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        self.stdout.write(self.style.NOTICE("Clearing addresses..."))
        start = time.perf_counter()

        cleaner = AddressCleaner()
        cleaner.cleen_users()

        total_time = time.perf_counter() - start

        remaining_address = address.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Addresses cleared in {total_time:.3f}s. "
                f"Remaining addresses: {remaining_address:,}"
            )
        )
