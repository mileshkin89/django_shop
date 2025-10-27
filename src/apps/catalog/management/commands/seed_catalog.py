from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from seed_data.catalog.catalog import ProductGenerator


class Command(BaseCommand):
    """
    Django management command for loading product data into the database.
    It reads data from `products.csv` and `images.csv`, validates rows,
    skips duplicates/invalid entries, and inserts products in chunks.
    """

    help = "Load data from products.csv and images.csv into the database"

    def add_arguments(self, parser):
        """
        Add command-line arguments for custom CSV file paths.
        """
        parser.add_argument(
            "--products",
            dest="products_csv",
            type=str,
            default=settings.PRODUCTS_DATASET_CSV,
            help="Path to `products.csv`"
        )
        parser.add_argument(
            "--images",
            dest="images_csv",
            type=str,
            default=settings.IMAGES_DATASET_CSV,
            help="Path to `images.csv`"
        )
        parser.add_argument(
            "--batch-size",
            dest="batch_size",
            type=int,
            default=1000,
            help="How many products write to DB at once (default: 1000)",
        )

    def handle(self, *args, **options):
        """
        Entry point for the management command.
        Validates file existence and starts the loading process.
        """
        products_file = Path(options["products_csv"])
        images_file = Path(options["images_csv"])
        batch_size = options["batch_size"]

        if not products_file.exists():
            self.stderr.write(self.style.ERROR(f"File {products_file} not found"))
            return

        if not images_file.exists():
            self.stderr.write(self.style.ERROR(f"File {images_file} not found"))
            return

        self.stdout.write(self.style.NOTICE("Starting product loading..."))

        catalog = ProductGenerator(products_file, images_file, batch_size)
        catalog.seed_catalog()


