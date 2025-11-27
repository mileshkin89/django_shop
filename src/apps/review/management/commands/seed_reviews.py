import time

from django.core.management.base import BaseCommand

from apps.order.models import Order
from seed_data.review.review_rating_reply import ReviewGenerator


class Command(BaseCommand):
    help = 'Seeds the database with initial users reviews.'

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=5000,
            help="How many reviews to create at once (default: 5000)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]

        start = time.perf_counter()

        self.stdout.write(self.style.NOTICE(f"Starting to seed reviews and ratings..."))

        seed_data = ReviewGenerator(
            batch_size=batch_size,
        )
        seed_data.seed_reviews_ratings()
        seed_data.seed_replies()

        total = time.perf_counter() - start

        inserted_rows = Order.objects.count()

        self.stdout.write(self.style.SUCCESS(f"Reviews and ratings seeded in {total:.3f}s"))
        self.stdout.write(self.style.SUCCESS(f"Total inserted {inserted_rows} rows."))
