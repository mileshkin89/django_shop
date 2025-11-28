from rest_framework import serializers
from .models import Review, Reply
from ..accounts.serializers import UserSerializer


class ReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'author', 'review', 'text', 'created_at', 'updated_at']
        read_only_fields = ['author', 'review', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    review_replies = ReplySerializer(many=True, read_only=True)
    # replies = ReplySerializer(many=True, read_only=True, source='review_replies')
    author = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author', 'product', 'rating', 'text', 'review_replies', 'created_at', 'updated_at']
        read_only_fields = ['author', 'product', 'created_at', 'updated_at']
