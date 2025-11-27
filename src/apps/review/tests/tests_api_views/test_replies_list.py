from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.catalog.models import Product, ArticleType, SubCategory, MasterCategory
from apps.order.choices import StatusChoices
from apps.order.models import Order, OrderItem, Inventory
from apps.review.models import Review, Reply

User = get_user_model()


class RepliesListAPITestCase(APITestCase):
    """
    Integration tests for the RepliesListAPIView, covering retrieval
    and creation of replies for specific reviews with proper permission checks.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Prepare initial test data: users, product, reviews, and replies.
        """
        # Users
        cls.user = User.objects.create(
            username="user1",
            email="user1@test.com",
            password="pass1234"
        )
        cls.another_user = User.objects.create(
            username="user2",
            email="user2@test.com",
            password="pass1234"
        )
        cls.staff = User.objects.create(
            username="admin",
            email="admin@test.com",
            password="pass1234",
            is_staff=True
        )

        # Product
        cls.master_category = MasterCategory.objects.create(
            name="Test Master Category",
        )
        cls.sub_category = SubCategory.objects.create(
            master_category=cls.master_category,
            name="Test Sub Category",
        )
        cls.article_type = ArticleType.objects.create(
            sub_category=cls.sub_category,
            name="Test Article",
        )
        cls.product = Product.objects.create(
            article_type=cls.article_type,
            product_display_name="Test Product",
        )

        # Order
        cls.inventory = Inventory.objects.create(
            product=cls.product,
            stock=10,
            reserved=0,
            price=100,
        )
        cls.order = Order.objects.create(
            user=cls.user,
            status=StatusChoices.PAID,
            total_price=100,
        )
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            inventory=cls.inventory,
            quantity=1
        )

        # Review
        cls.review = Review.objects.create(
            product=cls.product,
            author=cls.user,
            text="Original review text",
            rating=5,
        )

        # Existing replies
        cls.reply_1 = Reply.objects.create(
            review=cls.review,
            author=cls.user,
            text="First reply to the review",
        )
        cls.reply_2 = Reply.objects.create(
            review=cls.review,
            author=cls.another_user,
            text="Second reply from another user",
        )

        # URL for replies list
        cls.url = reverse(
            "review:replies_list_add",
            kwargs={"slug": cls.product.slug, "comment_id": cls.review.id}
        )

    def authenticate(self, user):
        """
        Force-authenticate the test client as the given user.
        """
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def assertAuthenticationRequired(self, response):
        """
        Assert that the response indicates that authentication is required.
        """
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            f"Expected 401 or 403, but got {response.status_code}. Response: {response.data}"
        )
        self.assertIn('detail', response.data)

    # -----------------------------
    #           GET TESTS
    # -----------------------------

    def test_get_replies_unauthenticated(self):
        """
        Ensure that any user (including unauthenticated) can retrieve replies.
        """
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two replies created in setUpTestData

        # Verify reply data
        reply_texts = [reply['text'] for reply in response.data]
        self.assertIn("First reply to the review", reply_texts)
        self.assertIn("Second reply from another user", reply_texts)

    def test_get_replies_authenticated(self):
        """
        Ensure that authenticated users can retrieve replies.
        """
        self.authenticate(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_replies_empty_list(self):
        """
        Ensure that empty list is returned when there are no replies.
        """
        new_review = Review.objects.create(
            product=self.product,
            author=self.user,
            text="Review without replies",
            rating=4,
        )

        url = reverse(
            "review:replies_list_add",
            kwargs={"slug": self.product.slug, "comment_id": new_review.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])

    def test_get_replies_only_active(self):
        """
        Ensure that only active replies are returned.
        """
        inactive_reply = Reply.objects.create(
            review=self.review,
            author=self.user,
            text="Inactive reply",
            is_active=False
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only 2 active replies

        reply_texts = [reply['text'] for reply in response.data]
        self.assertNotIn("Inactive reply", reply_texts)

    def test_get_replies_nonexistent_review(self):
        """
        Ensure that 404 is returned when trying to get replies for non-existent review.
        """
        url = reverse(
            "review:replies_list_add",
            kwargs={"slug": self.product.slug, "comment_id": 99999}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_replies_inactive_review(self):
        """
        Ensure that 404 is returned when trying to get replies for inactive review.
        """
        inactive_review = Review.objects.create(
            product=self.product,
            author=self.user,
            text="Inactive review",
            rating=3,
            is_active=False
        )

        url = reverse(
            "review:replies_list_add",
            kwargs={"slug": self.product.slug, "comment_id": inactive_review.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    #           POST TESTS
    # -----------------------------

    def test_post_reply_authenticated_user(self):
        """
        Ensure that authenticated users can create replies.
        """
        self.authenticate(self.user)

        payload = {
            "text": "New reply from authenticated user"
        }

        initial_count = Reply.objects.count()
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "New reply from authenticated user")
        self.assertEqual(response.data["author"], self.user.id)

        # Verify the reply was created in database
        self.assertEqual(Reply.objects.count(), initial_count + 1)
        new_reply = Reply.objects.get(text="New reply from authenticated user")
        self.assertEqual(new_reply.author, self.user)
        self.assertEqual(new_reply.review, self.review)

    def test_post_reply_staff_user(self):
        """
        Ensure that staff users can create replies.
        """
        self.authenticate(self.staff)

        payload = {
            "text": "Staff user reply"
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Staff user reply")
        self.assertEqual(response.data["author"], self.staff.id)

    def test_post_reply_unauthenticated_user(self):
        """
        Ensure that unauthenticated users cannot create replies.
        """
        self.client.force_authenticate(user=None)

        payload = {
            "text": "Anonymous reply attempt"
        }

        initial_count = Reply.objects.count()
        response = self.client.post(self.url, payload)

        self.assertAuthenticationRequired(response)
        self.assertEqual(Reply.objects.count(), initial_count)  # No new reply created

    def test_post_reply_to_nonexistent_review(self):
        """
        Ensure that 404 is returned when trying to post to non-existent review.
        """
        self.authenticate(self.user)

        url = reverse(
            "review:replies_list_add",
            kwargs={"slug": self.product.slug, "comment_id": 99999}
        )

        payload = {
            "text": "Reply to non-existent review"
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_reply_to_inactive_review(self):
        """
        Ensure that 404 is returned when trying to post to inactive review.
        """
        inactive_review = Review.objects.create(
            product=self.product,
            author=self.user,
            text="Inactive review",
            rating=3,
            is_active=False
        )

        self.authenticate(self.user)

        url = reverse(
            "review:replies_list_add",
            kwargs={"slug": self.product.slug, "comment_id": inactive_review.id}
        )

        payload = {
            "text": "Reply to inactive review"
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_multiple_replies_same_user(self):
        """
        Ensure that the same user can post multiple replies to the same review.
        """
        self.authenticate(self.user)

        # First reply
        payload_1 = {"text": "First reply from user"}
        response_1 = self.client.post(self.url, payload_1)
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        # Second reply from same user
        payload_2 = {"text": "Second reply from same user"}
        response_2 = self.client.post(self.url, payload_2)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

        # Verify both replies exist
        user_replies = Reply.objects.filter(author=self.user, review=self.review)
        self.assertEqual(user_replies.count(), 3)  # 1 existing + 2 new
