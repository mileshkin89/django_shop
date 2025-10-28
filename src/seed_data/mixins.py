from typing import List, Tuple
from tqdm import tqdm

from django.db import transaction, IntegrityError


class SaveInDBMixin:
    """
    A reusable mixin that provides a convenient method for bulk inserting
    data into the database with optional styled console output.
    """
    def __init__(self, stdout=None, style=None):
        self.stderr = None
        self.stdout = stdout
        self.style = style

    def bulk_insert(self, data: list, model):
        try:
            with transaction.atomic():
                model.objects.bulk_create(data, ignore_conflicts=True)
            if self.stdout and self.style:
                self.stdout.write(self.style.SUCCESS(f"Saved {len(data)} rows in model {model.__name__}"))
        except IntegrityError as e:
            if self.stderr and self.style:
                self.stderr.write(self.style.ERROR(f"Insert error: {e}"))
            elif self.stdout and self.style:
                self.stdout.write(self.style.ERROR(f"Insert error: {e}"))


class DataCleanerMixin:
    """Generic method for deleting querysets with progress output."""
    def clean_data(self, data: List[Tuple[str, object]], description: str):
        with transaction.atomic():
            for label, qs in tqdm(data, desc=description):
                count, _ = qs.delete()
                tqdm.write(f"Deleted {count} rows from {label}")