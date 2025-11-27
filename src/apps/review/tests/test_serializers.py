from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.catalog.models import Product, ArticleType, SubCategory, MasterCategory
from apps.review.models import Review, Reply
from apps.review.serializers import ReviewSerializer, ReplySerializer

User = get_user_model()


class ReplySerializerTest(TestCase):
    """Tests for validating ReplySerializer behavior and field constraints."""
    def setUp(self):
        """Prepare a user, product, review, and related objects for testing."""
        self.user = User.objects.create(username="user1")
        # Product → Review → Reply
        master = MasterCategory.objects.create(name="M")
        sub = SubCategory.objects.create(master_category=master, name="S")
        article = ArticleType.objects.create(sub_category=sub, name="A")
        self.product = Product.objects.create(article_type=article, product_display_name="P")

        self.review = Review.objects.create(
            author=self.user,
            product=self.product,
            text="Nice!",
            rating=5
        )

    def test_reply_serializer_serialization(self):
        """Ensure ReplySerializer correctly serializes reply fields."""
        reply = Reply.objects.create(
            author=self.user,
            review=self.review,
            text="Thanks"
        )

        serializer = ReplySerializer(reply)
        data = serializer.data

        self.assertEqual(data["id"], reply.id)
        self.assertEqual(data["text"], reply.text)
        self.assertEqual(data["author"], reply.author.id)
        self.assertEqual(data["review"], reply.review.id)

    def test_reply_serializer_read_only_fields(self):
        """Ensure that 'author' and 'review' fields are marked as read-only."""
        serializer = ReplySerializer()

        self.assertIn("author", serializer.Meta.read_only_fields)
        self.assertIn("review", serializer.Meta.read_only_fields)

    def test_reply_serializer_validation(self):
        """Ensure the serializer validates required 'text' field."""
        serializer = ReplySerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)


class ReviewSerializerTest(TestCase):
    """Tests for validating ReviewSerializer behavior, nesting, and field rules."""
    def setUp(self):
        """Prepare a user and product for review serializer tests."""
        self.user = User.objects.create(username="user1")

        master = MasterCategory.objects.create(name="M")
        sub = SubCategory.objects.create(master_category=master, name="S")
        article = ArticleType.objects.create(sub_category=sub, name="A")
        self.product = Product.objects.create(article_type=article, product_display_name="P")

    def test_review_serializer_serialization_without_replies(self):
        """Ensure ReviewSerializer serializes a review without replies correctly."""
        review = Review.objects.create(
            author=self.user,
            product=self.product,
            rating=4,
            text="Good product"
        )

        serializer = ReviewSerializer(review)
        data = serializer.data

        self.assertEqual(data["id"], review.id)
        self.assertEqual(data["author"], review.author.id)
        self.assertEqual(data["product"], review.product.id)
        self.assertEqual(data["text"], "Good product")
        self.assertEqual(data["rating"], 4)
        self.assertEqual(data["review_replies"], [])

    def test_review_serializer_serialization_with_replies(self):
        """Ensure ReviewSerializer returns a nested list of reply objects."""
        review = Review.objects.create(
            author=self.user,
            product=self.product,
            rating=5,
            text="Nice!"
        )

        Reply.objects.create(author=self.user, review=review, text="Reply 1")
        Reply.objects.create(author=self.user, review=review, text="Reply 2")

        serializer = ReviewSerializer(review)
        data = serializer.data

        self.assertEqual(len(data["review_replies"]), 2)
        self.assertEqual(
            {r["text"] for r in data["review_replies"]},
            {"Reply 1", "Reply 2"}
        )

    def test_review_serializer_valid_data(self):
        """Ensure serializer accepts valid payload excluding read-only fields."""
        payload = {
            "rating": 3,
            "text": "Normal"
        }
        serializer = ReviewSerializer(data=payload)

        self.assertTrue(serializer.is_valid())

    def test_review_serializer_missing_text(self):
        """Ensure the serializer requires the 'text' field."""
        serializer = ReviewSerializer(data={"rating": 5})
        self.assertFalse(serializer.is_valid())
        self.assertIn("text", serializer.errors)

    def test_review_serializer_read_only_fields(self):
        """Ensure 'author' and 'product' fields are defined as read-only."""
        serializer = ReviewSerializer()

        self.assertIn("author", serializer.Meta.read_only_fields)
        self.assertIn("product", serializer.Meta.read_only_fields)
