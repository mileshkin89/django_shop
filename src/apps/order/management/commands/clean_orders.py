import time

from django.core.management.base import BaseCommand

from apps.order.models import Order
from seed_data.order.orders import OrderCleaner


class Command(BaseCommand):
    help = "Clear product orders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            dest="yes",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        count = Order.objects.count()

        self.stdout.write(
            self.style.NOTICE(
                f"{count:,} order rows will be deleted"
            )
        )

        if count == 0:
            self.stdout.write(self.style.WARNING("No orders to delete."))
            return

        confirmed = options["yes"]
        if not confirmed:
            answer = input(
                f"This will DELETE {count:,} order rows. "
                "Are you sure? Type 'yes' to continue: "
            )
            if answer.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        self.stdout.write(self.style.NOTICE("Clearing orders..."))
        start = time.perf_counter()

        cleaner = OrderCleaner()
        cleaner.clean_orders()

        total_time = time.perf_counter() - start

        remaining_orders = Order.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"orders cleared in {total_time:.3f}s. "
                f"Remaining orders: {remaining_orders:,}"
            )
        )
