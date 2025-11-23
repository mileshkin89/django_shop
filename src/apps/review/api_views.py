from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .mixins import PermissionMixin
from .models import Review, Reply
from .serializers import ReviewSerializer, ReplySerializer
from apps.catalog.models import Product


class ReviewsListAPIView(LoginRequiredMixin, PermissionMixin, APIView):
    def get_product(self):
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get(self, request, *args, **kwargs):
        product = self.get_product()

        comments = Review.objects.all().filter(
            product=product,
            is_active=True
        ).order_by('-created_at')

        serializer = ReviewSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=self.request.data)

        if not self._is_first_authors_comment():
            raise ValidationError(
                {"detail": "You have already left a review for this product."}
            )

        if not self._is_staff():
            if not self._is_author_product_buyer():
                raise ValidationError(
                    {"detail": "Only customers who purchased the product can leave a comment."}
                )

        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['author'] = self.request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailAPIView(LoginRequiredMixin, PermissionMixin, APIView):
    def get_product(self):
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_object(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs['comment_id'],
            product=self.get_product(),
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = ReviewSerializer(comment)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        if not self._is_user_author_or_staff():
            raise ValidationError(
                {"detail": "Only the review author can perform this action."}
            )

        comment = self.get_object()
        serializer = ReviewSerializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if not self._is_user_author_or_staff():
            raise ValidationError(
                {"detail": "Only the review author can perform this action."}
            )

        comment = self.get_object()

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepliesListAPIView(LoginRequiredMixin, PermissionMixin, APIView):
    def get_product(self):
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_comment(self):
        return get_object_or_404(
            Review,
            product=self.get_product(),
            pk=self.kwargs['comment_id'],
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        replies = Reply.objects.filter(
            review=self.get_comment(),
            is_active=True
        ).all()

        serializer = ReplySerializer(replies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ReplySerializer(data=self.request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['author'] = self.request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyDetailAPIView(LoginRequiredMixin, PermissionMixin, APIView):
    def get_product(self):
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_comment(self):
        return get_object_or_404(
            Review,
            product=self.get_product(),
            pk=self.kwargs['comment_id'],
            is_active=True
        )

    def get_object(self):
        return get_object_or_404(
            Reply,
            pk=self.kwargs['reply_id'],
            review=self.get_comment(),
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        reply = self.get_object()
        serializer = ReplySerializer(reply)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        if not self._is_user_author_or_staff():
            raise ValidationError(
                {"detail": "Only the review author can perform this action."}
            )

        reply = self.get_object()
        serializer = ReplySerializer(reply, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        if not self._is_user_author_or_staff():
            raise ValidationError(
                {"detail": "Only the review author can perform this action."}
            )

        reply = self.get_object()

        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
