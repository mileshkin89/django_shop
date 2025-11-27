from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .mixins import PermissionMixin
from .models import Review, Reply
from .serializers import ReviewSerializer, ReplySerializer
from apps.catalog.models import Product


class ReviewsListAPIView(PermissionMixin, APIView):
    """
    Handles listing and creating product reviews.
    GET requests are publicly accessible, while POST requests require authentication
    and additional permission checks (buyer-only rule, one-review-per-user rule).
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self):
        """
        Retrieve and return the product associated with the request's slug.
        Ensures the product exists and is active.
        """
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get(self, request, *args, **kwargs):
        """
        Return a list of active reviews for the requested product,
        ordered by creation date (newest first).
        """
        product = self.get_product()

        comments = Review.objects.all().filter(
            product=product,
            is_active=True
        ).order_by('-created_at')

        serializer = ReviewSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a new review for the product.
        Applies business rules:
        - Staff users can always comment.
        - Regular users must have purchased the product.
        - Users may submit only one review per product.
        """
        serializer = ReviewSerializer(data=self.request.data)

        if not self._is_staff():
            if not self._is_author_product_buyer():
                raise ValidationError(
                    {"detail": "Only customers who purchased the product can leave a comment."}
                )

            if not self._is_first_authors_comment():
                raise ValidationError(
                    {"detail": "You have already left a review for this product."}
                )

        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['author'] = self.request.user
            validated_data['product'] = self.get_product()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailAPIView(PermissionMixin, APIView):
    """
    Handles retrieving, updating, and deleting a single product review.
    GET is publicly accessible; PATCH and DELETE require authentication
    and additional author/staff permission checks.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self):
        """
        Retrieve and return the active product associated with the request's slug.
        Raises 404 if the product does not exist or is inactive.
        """
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_object(self):
        """
        Retrieve and return the requested active review for the given product.
        Raises 404 if the review does not exist, is inactive, or does not belong to the product.
        """
        return get_object_or_404(
            Review,
            pk=self.kwargs['comment_id'],
            product=self.get_product(),
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        """
        Return serialized data for the requested review.
        """
        comment = self.get_object()
        serializer = ReviewSerializer(comment)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        Partially update the review.
        Only the review author or a staff user is allowed to perform this action.
        """
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
        """
        Delete the review.
        Only the review author or a staff user is allowed to perform this action.
        """
        if not self._is_user_author_or_staff():
            raise ValidationError(
                {"detail": "Only the review author can perform this action."}
            )

        comment = self.get_object()

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RepliesListAPIView(PermissionMixin, APIView):
    """
    Handles listing and creating replies for a specific product review.
    GET is publicly accessible; POST requires authentication.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self):
        """
        Retrieve and return the active product by slug.
        Raises 404 if the product does not exist or is inactive.
        """
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_comment(self):
        """
        Retrieve and return the active review related to the product.
        Raises 404 if the review does not exist, is inactive,
        or does not belong to the product.
        """
        return get_object_or_404(
            Review,
            product=self.get_product(),
            pk=self.kwargs['comment_id'],
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        """
        Return a list of active replies for the specified review.
        """
        replies = Reply.objects.filter(
            review=self.get_comment(),
            is_active=True
        ).all()

        serializer = ReplySerializer(replies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a new reply for the specified review.
        The authenticated user becomes the reply's author.
        """
        serializer = ReplySerializer(data=self.request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['author'] = self.request.user
            validated_data['review'] = self.get_comment()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyDetailAPIView(PermissionMixin, APIView):
    """
    Handles retrieving, updating, and deleting a single reply to a product review.
    GET is publicly accessible; PATCH and DELETE require authentication
    and author/staff permissions.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self):
        """
        Retrieve and return the active product associated with the slug.
        Raises 404 if not found or inactive.
        """
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_comment(self):
        """
        Retrieve and return the active review belonging to the product.
        Raises 404 if not found or inactive.
        """
        return get_object_or_404(
            Review,
            product=self.get_product(),
            pk=self.kwargs['comment_id'],
            is_active=True
        )

    def get_object(self):
        """
        Retrieve and return the active reply associated with the review.
        Raises 404 if the reply does not exist, is inactive,
        or does not belong to the review.
        """
        return get_object_or_404(
            Reply,
            pk=self.kwargs['reply_id'],
            review=self.get_comment(),
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        """
        Retrieve and return the active reply associated with the review.
        Raises 404 if the reply does not exist, is inactive,
        or does not belong to the review.
        """
        reply = self.get_object()
        serializer = ReplySerializer(reply)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        Partially update the reply.
        Only the reply author or a staff user is permitted to perform this action.
        """
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
        """
        Delete the reply.
        Only the reply author or a staff user is permitted to perform this action.
        """
        if not self._is_user_author_or_staff():
            raise ValidationError(
                {"detail": "Only the review author can perform this action."}
            )

        reply = self.get_object()

        reply.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
