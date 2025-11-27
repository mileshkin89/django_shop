from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.catalog.models import Product, ArticleType, SubCategory, MasterCategory
from apps.order.choices import StatusChoices
from apps.order.models import Order, OrderItem, Inventory
from apps.review.models import Review, Reply

User = get_user_model()


class ReplyDetailAPITestCase(APITestCase):
    """
    Integration tests for the ReplyDetailAPIView, covering retrieval,
    updating, and deletion of individual replies with proper permission checks.
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

        # Review
        cls.review = Review.objects.create(
            product=cls.product,
            author=cls.user,
            text="Original review text",
            rating=5,
        )

        # Reply
        cls.reply = Reply.objects.create(
            review=cls.review,
            author=cls.user,
            text="Original reply text",
        )

        # Another reply by different user for testing
        cls.another_reply = Reply.objects.create(
            review=cls.review,
            author=cls.another_user,
            text="Another user's reply",
        )

        # URL for the specific reply
        cls.url = reverse(
            "review:reply_retrieve_edit_delete",
            kwargs={
                "slug": cls.product.slug,
                "comment_id": cls.review.id,
                "reply_id": cls.reply.id
            }
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

    def test_get_reply_unauthenticated(self):
        """
        Ensure that any user (including unauthenticated) can retrieve a reply.
        """
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Original reply text")
        self.assertEqual(response.data["author"], self.user.id)

    def test_get_reply_authenticated(self):
        """
        Ensure that authenticated users can retrieve replies.
        """
        self.authenticate(self.another_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Original reply text")

    def test_get_nonexistent_reply(self):
        """
        Ensure that retrieving a non-existent reply returns 404.
        """
        url = reverse(
            "review:reply_retrieve_edit_delete",
            kwargs={
                "slug": self.product.slug,
                "comment_id": self.review.id,
                "reply_id": 99999
            }
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_reply_from_different_review(self):
        """
        Ensure that reply IDs are scoped to their specific reviews.
        """
        # Create another review
        another_review = Review.objects.create(
            product=self.product,
            author=self.another_user,
            text="Another review",
            rating=4,
        )

        # Try to access the reply using the other review's ID
        url = reverse(
            "review:reply_retrieve_edit_delete",
            kwargs={
                "slug": self.product.slug,
                "comment_id": another_review.id,
                "reply_id": self.reply.id
            }
        )

        response = self.client.get(url)

        # Should return 404 because the reply doesn't belong to this review
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_reply(self):
        """
        Ensure that inactive replies cannot be retrieved.
        """
        self.reply.is_active = False
        self.reply.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    #           PATCH TESTS
    # -----------------------------

    def test_patch_reply_by_author(self):
        """
        Ensure that the reply author can update their own reply.
        """
        self.authenticate(self.user)

        payload = {
            "text": "Updated reply text"
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Updated reply text")

        # Verify the update in database
        self.reply.refresh_from_db()
        self.assertEqual(self.reply.text, "Updated reply text")

    def test_patch_reply_by_staff(self):
        """
        Ensure that staff users can update any reply.
        """
        self.authenticate(self.staff)

        payload = {
            "text": "Staff updated this reply",
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Staff updated this reply")

        # Verify the update in database
        self.reply.refresh_from_db()
        self.assertEqual(self.reply.text, "Staff updated this reply")

    def test_patch_reply_by_non_author(self):
        """
        Ensure that a user who is not the author cannot update the reply.
        """
        self.authenticate(self.another_user)

        payload = {
            "text": "Trying to update someone else's reply",
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("author", response.data["detail"].lower())

        # Verify the reply was NOT updated
        self.reply.refresh_from_db()
        self.assertEqual(self.reply.text, "Original reply text")

    def test_patch_reply_unauthenticated(self):
        """
        Ensure that unauthenticated users cannot update replies.
        """
        self.client.force_authenticate(user=None)

        payload = {
            "text": "Anonymous update attempt",
        }

        response = self.client.patch(self.url, payload)

        self.assertAuthenticationRequired(response)

        # Verify the reply was NOT updated
        self.reply.refresh_from_db()
        self.assertEqual(self.reply.text, "Original reply text")

    def test_partial_update_reply(self):
        """
        Ensure that partial updates work correctly (PATCH method).
        """
        self.authenticate(self.user)

        payload = {
            "text": "Only text updated",
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Only text updated")

        # Verify partial update in database
        self.reply.refresh_from_db()
        self.assertEqual(self.reply.text, "Only text updated")

    # -----------------------------
    #           DELETE TESTS
    # -----------------------------

    def test_delete_reply_by_author(self):
        """
        Ensure that the reply author can delete their own reply.
        """
        self.authenticate(self.user)

        initial_count = Reply.objects.count()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reply.objects.count(), initial_count - 1)

        # Verify the reply is deleted
        with self.assertRaises(Reply.DoesNotExist):
            Reply.objects.get(id=self.reply.id)

    def test_delete_reply_by_staff(self):
        """
        Ensure that staff users can delete any reply.
        """
        self.authenticate(self.staff)

        initial_count = Reply.objects.count()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Reply.objects.count(), initial_count - 1)

    def test_delete_reply_by_non_author(self):
        """
        Ensure that a user who is not the author cannot delete the reply.
        """
        self.authenticate(self.another_user)

        initial_count = Reply.objects.count()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("author", response.data["detail"].lower())
        self.assertEqual(Reply.objects.count(), initial_count)

    def test_delete_reply_unauthenticated(self):
        """
        Ensure that unauthenticated users cannot delete replies.
        """
        self.client.force_authenticate(user=None)

        initial_count = Reply.objects.count()
        response = self.client.delete(self.url)

        self.assertAuthenticationRequired(response)
        self.assertEqual(Reply.objects.count(), initial_count)

    def test_delete_nonexistent_reply(self):
        """
        Ensure that deleting a non-existent reply returns 404.
        """
        self.authenticate(self.user)

        url = reverse(
            "review:reply_retrieve_edit_delete",
            kwargs={
                "slug": self.product.slug,
                "comment_id": self.review.id,
                "reply_id": 99999
            }
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_inactive_reply(self):
        """
        Ensure that inactive replies cannot be deleted.
        """
        self.reply.is_active = False
        self.reply.save()

        self.authenticate(self.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    #       EDGE CASE TESTS
    # -----------------------------

    def test_access_with_inactive_review(self):
        """
        Ensure that replies cannot be accessed when the parent review is inactive.
        """
        # Make review inactive
        self.review.is_active = False
        self.review.save()

        self.authenticate(self.user)

        # Try to GET reply
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to PATCH reply
        payload = {"text": "Trying to update reply with inactive review"}
        response = self.client.patch(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to DELETE reply
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
