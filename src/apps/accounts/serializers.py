from rest_framework import serializers
from .models import User, ShippingAddress


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            'id',
            'user',
            'shipping_address'
        ]
        read_only_fields = [
            'user',
            'shipping_address'
        ]


class UserSerializer(serializers.ModelSerializer):
    shipping_address = ShippingAddressSerializer(
        source='shipping_addresses.first',
        read_only=True,
        # many=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'phone_number',
            'last_login',
            'is_superuser',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'date_joined',
            'shipping_address'
        ]
        read_only_fields = [
            'username',
            'phone_number',
            'last_login',
            'is_superuser',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'date_joined',
            'shipping_address'
        ]


