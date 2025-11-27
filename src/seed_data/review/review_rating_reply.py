import random
from typing import List
from tqdm import tqdm

from django.db.models import Prefetch

from apps.catalog.models import Product
from apps.review.models import Review, Reply
from seed_data.mixins import SaveInDBMixin, DataCleanerMixin
from apps.accounts.models import User
from seed_data.review.random_replies import get_random_replies
from seed_data.review.random_review_rating import get_random_review_rating


class ReviewGenerator(SaveInDBMixin):
    def __init__(self, batch_size: int = 5000):
        super().__init__()
        self.batch_size = batch_size

    def seed_reviews_ratings(self):
        users = User.objects.prefetch_related(
            Prefetch(
                'user_orders__order_items__product',
                queryset=Product.objects.filter(is_active=True).only('id'),
            )
        ).all()

        all_reviews: List[Review] = []

        for user in tqdm(users, desc="Seeding reviews and ratings"):
            # unique products purchased by the user
            products = {
                item.product
                for order in user.user_orders.all()
                if order.status in ['Paid', 'Shipped', 'Delivered', 'Completed']
                for item in order.order_items.all()
            }

            for product in products:
                review_text, rating = get_random_review_rating()

                review = Review(
                    author=user,
                    product=product,
                    text=review_text,
                    rating=rating,
                )
                all_reviews.append(review)

        self._bulk_create(all_reviews, Review, batch_size=self.batch_size)

    def seed_replies(self):
        reviews = list(Review.objects.all())

        all_replies: List[Reply] = []
        i = 0

        for review in tqdm(reviews, desc="Seeding replies"):
            i += 1

            if i != 7:
                continue

            reply_count = random.randint(1, 5)

            for _ in range(reply_count):
                reply_text = get_random_replies()

                all_replies.append(
                    Reply(
                        author=review.author,
                        review=review,
                        text=reply_text,
                    )
                )
                i = 0

        self._bulk_create(all_replies, Reply, batch_size=self.batch_size)


class ReviewCleaner(DataCleanerMixin):
    def __init__(self):
        self._data_to_delete = [
            ("reviews", Review.objects.all()),
            ("replies", Reply.objects.all()),
        ]

        self.desc = "Cleaning reviews, ratings and replies"

    def clean_reviews(self):
        self.clean_data(self._data_to_delete, self.desc)
