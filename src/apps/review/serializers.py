from rest_framework import serializers
from .models import Review, Reply


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['id', 'author', 'review', 'text']


class ReviewSerializer(serializers.ModelSerializer):
    review_replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author', 'product', 'rating', 'text', 'review_replies']
