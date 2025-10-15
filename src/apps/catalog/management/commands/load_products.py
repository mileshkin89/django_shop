import csv
from pathlib import Path

from tqdm import tqdm

from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError

from apps.catalog.models import (
    MasterCategory, SubCategory, ArticleType,
    BaseColour, Season, UsageType, Product
)
from django.conf import settings


# Number of rows to load per chunk
CHUNK_SIZE = 500


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
            type=str,
            default=settings.PRODUCTS_DATASET_CSV,
            help="Path to products.csv"
        )
        parser.add_argument(
            "--images",
            type=str,
            default=settings.IMAGES_DATASET_CSV,
            help="Path to images.csv"
        )

    def handle(self, *args, **options):
        """
        Entry point for the management command.
        Validates file existence and starts the loading process.
        """
        products_file = Path(options["products"])
        images_file = Path(options["images"])

        if not products_file.exists():
            self.stderr.write(self.style.ERROR(f"File {products_file} not found"))
            return
        if not images_file.exists():
            self.stderr.write(self.style.WARNING(f"File {images_file} not found"))
            images = {}
        else:
            images = self.load_images(images_file)

        self.stdout.write(self.style.NOTICE("Starting product loading..."))

        self.load_products(products_file, images)

    def validate_row(self, row):
        """
        Validate a CSV row for required fields and correct types.
        Returns True if the row is valid, otherwise False.
        """
        required_fields = [
            "product_id", "gender", "master_category",
            "sub_category", "article_type",
            "base_colour", "season", "year",
            "usage", "product_display_name"
        ]

        # check for missing required fields
        for field in required_fields:
            if not row.get(field) or row[field].strip() == "":
                return False

        # product_id must be an integer
        try:
            int(row["product_id"])
        except ValueError:
            return False

        return True

    def load_images(self, file_path):
        """
        Load image data from images.csv into a dictionary.
        Returns {product_id: image_url}.
        """
        images = {}
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                filename = row.get("filename")
                link = row.get("link")
                if filename and link:
                    product_id = filename.replace(".jpg", "")
                    images[product_id] = link
        return images

    def load_products(self, file_path, images):
        """
        Load products from products.csv.
        Validate each row, skip duplicates/invalid rows,
        and bulk insert products in chunks.
        """
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            total = sum(1 for _ in open(file_path, encoding="utf-8")) - 1  # total rows

            batch = []
            seen_ids = set(Product.objects.values_list("product_id", flat=True))

            for i, row in tqdm(enumerate(reader, start=1), total=total):
                if not self.validate_row(row):
                    self.stderr.write(self.style.WARNING(
                        f"Skipped row {i}: invalid data → {row}"
                    ))
                    continue

                product_id = int(row["product_id"])
                if product_id in seen_ids:
                    self.stderr.write(self.style.WARNING(
                        f"Skipped row {i}: duplicate product_id={product_id}"
                    ))
                    continue

                # get or create reference objects
                master_category, _ = MasterCategory.objects.get_or_create(
                    name=row["master_category"].strip()
                )
                sub_category, _ = SubCategory.objects.get_or_create(
                    master_category=master_category,
                    name=row["sub_category"].strip()
                )
                article_type, _ = ArticleType.objects.get_or_create(
                    sub_category=sub_category,
                    name=row["article_type"].strip()
                )
                base_colour, _ = BaseColour.objects.get_or_create(
                    name=row["base_colour"].strip()
                )
                season, _ = Season.objects.get_or_create(
                    name=row["season"].strip()
                )
                usage, _ = UsageType.objects.get_or_create(
                    name=row["usage"].strip()
                )

                # build Product object
                batch.append(Product(
                    product_id=product_id,
                    gender=row["gender"].strip(),
                    year=int(row["year"]),
                    product_display_name=row["product_display_name"].strip(),
                    image_url=images.get(str(product_id), ""),
                    article_type=article_type,
                    base_colour=base_colour,
                    season=season,
                    usage_type=usage,
                ))
                seen_ids.add(product_id)

                # bulk insert when chunk is full
                if len(batch) >= CHUNK_SIZE:
                    self.bulk_insert(batch)
                    batch = []

            # insert remaining products
            if batch:
                self.bulk_insert(batch)

    def bulk_insert(self, batch):
        """
        Perform a bulk insert of a batch of products inside a transaction.
        """
        try:
            with transaction.atomic():
                Product.objects.bulk_create(batch, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Saved {len(batch)} products"))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Insert error: {e}"))
