from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class BaseReview(models.Model):
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='user_%(class)ss'
    )
    text = models.TextField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Review(BaseReview):
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='product_reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    class Meta:
        ordering = ['-updated_at']

    def has_reply(self) -> bool:
        return self.review_replies.exists()

    def get_replies(self):
        return self.review_replies.all()

    def __str__(self):
        return f"{self.author.username} - {self.product.product_display_name}"


class Reply(BaseReview):
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='user_replies',
    )
    review = models.ForeignKey(
        'review.Review',
        on_delete=models.CASCADE,
        related_name='review_replies',
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.review.text} - {self.text}"
