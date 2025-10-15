from django.db import transaction, IntegrityError


class SaveInDBMixin:
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