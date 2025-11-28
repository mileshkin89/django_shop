from django.conf import settings
from django.test import TestCase

from apps.accounts.models import User, ShippingAddress
from apps.accounts.serializers import ShippingAddressSerializer, UserSerializer


class ShippingAddressSerializerTest(TestCase):
    """Tests for ShippingAddressSerializer behavior and data validation."""
    def setUp(self):
        self.user = User.objects.create(
            email="test@mail.com",
            username="testuser",
        )
        self.address = ShippingAddress.objects.create(
            user=self.user,
            shipping_address="Some address"
        )

    def test_serialization(self):
        """Ensure the serializer returns correct serialized ShippingAddress data."""
        serializer = ShippingAddressSerializer(self.address)
        data = serializer.data

        self.assertEqual(data["id"], self.address.id)
        self.assertEqual(data["user"], self.user.id)
        self.assertEqual(data["shipping_address"], "Some address")

    def test_read_only_fields(self):
        """Verify that 'user' and 'shipping_address' fields are marked as read-only."""
        serializer = ShippingAddressSerializer()

        self.assertIn("user", serializer.Meta.read_only_fields)
        self.assertIn("shipping_address", serializer.Meta.read_only_fields)

    def test_validation_fails_when_attempting_to_write_read_only_fields(self):
        """Ensure attempts to modify read-only fields are ignored during update."""
        serializer = ShippingAddressSerializer(
            self.address,
            data={"user": 999, "shipping_address": "Another"},
            partial=True
        )

        self.assertTrue(serializer.is_valid())

        obj = serializer.save()

        self.assertEqual(obj.user.id, self.user.id)
        self.assertEqual(obj.shipping_address, "Some address")


class UserSerializerTest(TestCase):
    """Tests for UserSerializer serialization and field permissions."""
    def setUp(self):
        self.user = User.objects.create(
            email="test@mail.com",
            username="user1",
            first_name="John",
            last_name="Doe",
            phone_number="12345"
        )
        # self.shipping_address created in `signals.py`

    def test_serialization_basic(self):
        """Ensure UserSerializer correctly returns basic user fields."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")

    def test_nested_shipping_address_serialization(self):
        """Ensure the serializer includes nested read-only shipping_address data."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertIn("shipping_address", data)
        self.assertEqual(data["shipping_address"]["id"], 1)
        self.assertEqual(data["shipping_address"]["shipping_address"], settings.DEFAULT_SHIPPING_ADDRESS)

    def test_read_only_fields(self):
        """Verify that required fields are included in Meta.read_only_fields."""
        serializer = UserSerializer()

        ro = serializer.Meta.read_only_fields

        self.assertIn("username", ro)
        self.assertIn("phone_number", ro)
        self.assertIn("is_superuser", ro)
        self.assertIn("is_active", ro)
        self.assertIn("date_joined", ro)
        self.assertIn("shipping_address", ro)

    def test_attempt_to_update_read_only_fields(self):
        """Ensure read-only fields are not modified during partial updates."""
        old_username = self.user.username
        old_first_name = self.user.first_name

        serializer = UserSerializer(
            self.user,
            data={
                "username": "new_username",
                "first_name": "NewName"
            },
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.username, old_username)
        self.assertEqual(updated_user.first_name, old_first_name)

    def test_updatable_fields(self):
        """Ensure writable fields such as 'email' can be updated successfully."""
        serializer = UserSerializer(
            self.user,
            data={"email": "updated@mail.com"},
            partial=True
        )

        self.assertTrue(serializer.is_valid())
        updated = serializer.save()

        self.assertEqual(updated.email, "updated@mail.com")
