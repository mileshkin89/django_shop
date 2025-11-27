from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.catalog.models import Product, ArticleType, SubCategory, MasterCategory
from apps.order.choices import StatusChoices
from apps.order.models import Order, OrderItem, Inventory
from apps.review.models import Review

User = get_user_model()


class ReviewsListAPITestCase(APITestCase):
    """
    Integration tests for the Review API, covering authentication,
    permission logic, and business rules for creating and retrieving reviews.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Prepare initial test data: users, product hierarchy, inventory,
        orders, and an existing review used across test cases.
        """
        # Users
        cls.user = User.objects.create(
            username="user1",
            email="user1@test.com",
            password="pass1234"
        )

        cls.user_not_buyer = User.objects.create(
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

        # Order for user1 => buyer
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

        # Existing review
        cls.existing_review = Review.objects.create(
            product=cls.product,
            author=cls.user,
            text="Good product!",
            rating=5,
        )

        cls.url = reverse("review:comments_list_add", kwargs={"slug": cls.product.slug})

    def authenticate(self, user):
        """
        Force-authenticate the test client as the given user.
        Simplifies authentication for DRF permission-based views.
        """
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def assertAuthenticationRequired(self, response):
        """
        Assert that the response indicates that authentication is required.
        Validates both status code (401/403) and presence of a 'detail' message.
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

    def test_get_reviews(self):
        """
        Ensure that reviews can be retrieved by an unauthenticated user.
        Confirms response structure and that the existing review is returned.
        """
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["text"], "Good product!")
        self.assertEqual(response.data[0]["rating"], 5)

    def test_get_reviews_only_active(self):
        """
        Ensure that only active reviews are returned.
        """
        Review.objects.create(
            product=self.product,
            author=self.staff,
            text="Inactive review",
            rating=1,
            is_active=False,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only 1 active review

        review_texts = [review['text'] for review in response.data]
        self.assertNotIn("Inactive review", review_texts)

        # -----------------------------
        #           POST TESTS
        # -----------------------------

    def test_post_review_unauthenticated_user(self):
        """
        Ensure that an unauthenticated user cannot create a review.
        Validates error response and confirms no new review is created.
        """
        self.client.force_authenticate(user=None)

        payload = {
            "text": "Trying to post without login",
            "rating": 3
        }

        initial_count = Review.objects.count()
        response = self.client.post(self.url, payload)

        self.assertAuthenticationRequired(response)

        expected_error_keys = ['detail']
        for key in expected_error_keys:
            self.assertIn(key, response.data)

        self.assertEqual(Review.objects.count(), initial_count)
        new_reviews = Review.objects.filter(text=payload["text"])
        self.assertFalse(new_reviews.exists())

    def test_post_review_after_logout(self):
        """
        Ensure that a user who logs out cannot create a review.
        Confirms correct authentication error messaging.
        """
        self.authenticate(self.user)
        self.client.force_authenticate(user=None)

        payload = {
            "text": "Comment after logout",
            "rating": 4
        }

        response = self.client.post(self.url, payload)

        self.assertAuthenticationRequired(response)

        error_message = response.data.get("detail", "").lower()
        self.assertTrue(
            any(word in error_message for word in ["authentication", "login", "credentials"]),
            f"Error message should indicate authentication issue: {error_message}"
        )

    def test_user_can_leave_first_review(self):
        """
        Ensure that a user who has purchased the product can leave
        their first review successfully.
        """
        order = Order.objects.create(
            user=self.user_not_buyer,
            total_price=100,
            status=StatusChoices.PAID
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            inventory=self.inventory,
            quantity=1
        )

        self.authenticate(self.user_not_buyer)

        payload = {"text": "My first comment!", "rating": 5}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "My first comment!")
        self.assertEqual(Review.objects.filter(author=self.user_not_buyer, product=self.product).count(), 1)

    def test_user_cannot_leave_second_review(self):
        """
        Ensure that a user cannot leave more than one review for the same product.
        """
        self.authenticate(self.user)

        payload = {"text": "Trying again"}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already", response.data["detail"].lower())

    def test_not_buyer_cannot_comment(self):
        """
        Ensure that a user who has not purchased the product cannot
        leave a review.
        """
        self.authenticate(self.user_not_buyer)

        payload = {"text": "I want comment but I did not buy"}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchased", response.data["detail"].lower())

    def test_staff_can_comment_without_buying(self):
        """
        Ensure that staff users are allowed to leave reviews even if
        they have not purchased the product.
        """
        self.authenticate(self.staff)

        payload = {"text": "Admin comment", "rating": 5}

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "Admin comment")
