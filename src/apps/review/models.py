from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Index, Q


class Review(models.Model):
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='user_reviews',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='product_reviews',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    comment = models.TextField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        indexes = [
            Index(
                fields=['author', 'product'],
                name='unique_root_review',
                condition=Q(parent__isnull=True),
            )
        ]

    def __str__(self):
        return f"{self.author.username} - {self.product.product_display_name}"

    def clean(self):
        super().clean()

        if self.parent and self.parent.parent:
            raise ValidationError('Only one level of nesting is allowed.')

        if self.parent is None and self.rating is None:
            raise ValidationError('Root comments must include a rating.')

        if self.parent is not None and self.rating is not None:
            raise ValidationError('Replies cannot have a rating.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        return self.parent is not None

    def get_replies(self):
        return self.replies.filter(is_active=True).order_by('created_at')
