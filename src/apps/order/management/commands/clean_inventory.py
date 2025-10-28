import time

from django.core.management.base import BaseCommand

from apps.order.models import Inventory
from seed_data.order.inventory import InventoryCleaner


class Command(BaseCommand):
    help = "Clear product inventory."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            dest="yes",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        count = Inventory.objects.count()

        self.stdout.write(
            self.style.NOTICE(
                f"{count:,} inventory rows will be deleted"
            )
        )

        if count == 0:
            self.stdout.write(self.style.WARNING("No inventory to delete."))
            return

        confirmed = options["yes"]
        if not confirmed:
            answer = input(
                f"This will DELETE {count:,} inventory rows. "
                "Are you sure? Type 'yes' to continue: "
            )
            if answer.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        self.stdout.write(self.style.NOTICE("Clearing inventory..."))
        start = time.perf_counter()

        cleaner = InventoryCleaner()
        cleaner.clean_inventory()

        total_time = time.perf_counter() - start

        remaining_inventory = Inventory.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"inventory cleared in {total_time:.3f}s. "
                f"Remaining inventory: {remaining_inventory:,}"
            )
        )
