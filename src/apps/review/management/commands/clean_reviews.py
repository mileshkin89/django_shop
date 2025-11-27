import time

from django.core.management.base import BaseCommand

from apps.review.models import Review
from seed_data.review.review_rating_reply import ReviewCleaner


class Command(BaseCommand):
    help = "Clear product reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            dest="yes",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        count = Review.objects.count()

        self.stdout.write(
            self.style.NOTICE(
                f"{count:,} review rows will be deleted"
            )
        )

        if count == 0:
            self.stdout.write(self.style.WARNING("No reviews to delete."))
            return

        confirmed = options["yes"]
        if not confirmed:
            answer = input(
                f"This will DELETE {count:,} review rows. "
                "Are you sure? Type 'yes' to continue: "
            )
            if answer.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        self.stdout.write(self.style.NOTICE("Clearing reviews..."))
        start = time.perf_counter()

        cleaner = ReviewCleaner()
        cleaner.clean_reviews()

        total_time = time.perf_counter() - start

        remaining_orders = Review.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"reviews cleared in {total_time:.3f}s. "
                f"Remaining reviews: {remaining_orders:,}"
            )
        )
