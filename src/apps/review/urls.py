from django.urls import path

from . import api_views

app_name = "review"

urlpatterns = [
    path(
        'api/products/<slug:slug>/comments/<int:comment_id>/',
        api_views.ReviewDetailAPIView.as_view(),
        name='comment_retrieve_edit_delete'
    ),
    path(
        'api/products/<slug:slug>/comments/',
        api_views.ReviewsListAPIView.as_view(),
        name='comments_list_add'
    ),

    path(
        'api/products/<slug:slug>/comments/<int:comment_id>/replies/<int:reply_id>/',
        api_views.ReplyDetailAPIView.as_view(),
        name='reply_retrieve_edit_delete'
    ),
    path(
        'api/products/<slug:slug>/comments/<int:comment_id>/replies/',
        api_views.RepliesListAPIView.as_view(),
        name='replies_list_add'
    ),
]
