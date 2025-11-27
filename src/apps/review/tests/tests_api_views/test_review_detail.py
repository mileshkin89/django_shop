from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.catalog.models import Product, ArticleType, SubCategory, MasterCategory
from apps.order.choices import StatusChoices
from apps.order.models import Order, OrderItem, Inventory
from apps.review.models import Review

User = get_user_model()


class ReviewDetailAPITestCase(APITestCase):
    """
    Integration tests for the ReviewDetailAPIView, covering retrieval,
    updating, and deletion of individual reviews with proper permission checks.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Prepare initial test data: users, product hierarchy, inventory,
        orders, and reviews used across test cases.
        """
        # Users
        cls.user = User.objects.create(
            username="user1",
            email="user1@test.com",
            password="pass1234"
        )
        cls.user_not_author = User.objects.create(
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

        # Reviews
        cls.review = Review.objects.create(
            product=cls.product,
            author=cls.user,
            text="Original review text",
            rating=5,
        )
        cls.another_review = Review.objects.create(
            product=cls.product,
            author=cls.user_not_author,
            text="Another user's review",
            rating=4,
        )

        cls.url = reverse(
            "review:comment_retrieve_edit_delete",
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

    def test_get_review_unauthenticated(self):
        """
        Ensure that any user (including unauthenticated) can retrieve a review.
        """
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Original review text")
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["author"], self.user.id)

    def test_get_review_authenticated(self):
        """
        Ensure that authenticated users can retrieve reviews.
        """
        self.authenticate(self.user_not_author)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Original review text")

    def test_get_nonexistent_review(self):
        """
        Ensure that retrieving a non-existent review returns 404.
        """
        url = reverse(
            "review:comment_retrieve_edit_delete",
            kwargs={"slug": self.product.slug, "comment_id": 99999}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    #           PATCH TESTS
    # -----------------------------

    def test_patch_review_by_author(self):
        """
        Ensure that the review author can update their own review.
        """
        self.authenticate(self.user)

        payload = {
            "text": "Updated review text",
            "rating": 4
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Updated review text")
        self.assertEqual(response.data["rating"], 4)

        # Verify the update in database
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Updated review text")
        self.assertEqual(self.review.rating, 4)

    def test_patch_review_by_staff(self):
        """
        Ensure that staff users can update any review.
        """
        self.authenticate(self.staff)

        payload = {
            "text": "Staff updated this review",
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Staff updated this review")

        # Verify the update in database
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Staff updated this review")

    def test_patch_review_by_non_author(self):
        """
        Ensure that a user who is not the author cannot update the review.
        """
        self.authenticate(self.user_not_author)

        payload = {
            "text": "Trying to update someone else's review",
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("author", response.data["detail"].lower())

        # Verify the review was NOT updated
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Original review text")

    def test_patch_review_unauthenticated(self):
        """
        Ensure that unauthenticated users cannot update reviews.
        """
        self.client.force_authenticate(user=None)

        payload = {
            "text": "Anonymous update attempt",
        }

        response = self.client.patch(self.url, payload)

        self.assertAuthenticationRequired(response)

        # Verify the review was NOT updated
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Original review text")

    def test_partial_update_review(self):
        """
        Ensure that partial updates work correctly (PATCH method).
        """
        self.authenticate(self.user)

        # Update only text, keep original rating
        payload = {
            "text": "Only text updated",
        }

        response = self.client.patch(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Only text updated")
        self.assertEqual(response.data["rating"], 5)  # Original rating preserved

        # Verify partial update in database
        self.review.refresh_from_db()
        self.assertEqual(self.review.text, "Only text updated")
        self.assertEqual(self.review.rating, 5)

    # -----------------------------
    #           DELETE TESTS
    # -----------------------------

    def test_delete_review_by_author(self):
        """
        Ensure that the review author can delete their own review.
        """
        self.authenticate(self.user)

        initial_count = Review.objects.count()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), initial_count - 1)

        # Verify the review is deleted
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=self.review.id)

    def test_delete_review_by_staff(self):
        """
        Ensure that staff users can delete any review.
        """
        self.authenticate(self.staff)

        initial_count = Review.objects.count()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), initial_count - 1)

    def test_delete_review_by_non_author(self):
        """
        Ensure that a user who is not the author cannot delete the review.
        """
        self.authenticate(self.user_not_author)

        initial_count = Review.objects.count()
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("author", response.data["detail"].lower())
        self.assertEqual(Review.objects.count(), initial_count)  # Count unchanged

    def test_delete_review_unauthenticated(self):
        """
        Ensure that unauthenticated users cannot delete reviews.
        """
        self.client.force_authenticate(user=None)

        initial_count = Review.objects.count()
        response = self.client.delete(self.url)

        self.assertAuthenticationRequired(response)
        self.assertEqual(Review.objects.count(), initial_count)  # Count unchanged

    def test_delete_nonexistent_review(self):
        """
        Ensure that deleting a non-existent review returns 404.
        """
        self.authenticate(self.user)

        url = reverse(
            "review:comment_retrieve_edit_delete",
            kwargs={"slug": self.product.slug, "comment_id": 99999}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -----------------------------
    #       EDGE CASE TESTS
    # -----------------------------

    def test_update_inactive_review(self):
        """
        Ensure that inactive reviews cannot be retrieved or modified.
        """
        # Make review inactive
        self.review.is_active = False
        self.review.save()

        self.authenticate(self.user)

        # Try to GET inactive review
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to PATCH inactive review
        payload = {"text": "Trying to update inactive review"}
        response = self.client.patch(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to DELETE inactive review
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
