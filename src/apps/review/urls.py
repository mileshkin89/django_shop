from django.urls import path
from . import views

app_name = "review"

urlpatterns = [
    path('products/<slug:slug>/comment/add-comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('products/<slug:slug>/comment/<int:pk>/reply/', views.AddReplyView.as_view(), name='add_reply'),

    path('products/<slug:slug>/comment/<int:pk>/edit/', views.EditCommentView.as_view(), name='edit_comment'),
    path('products/<slug:slug>/reply/<int:pk>/edit/', views.EditReplyView.as_view(), name='edit_reply'),

    path('products/<slug:slug>/comment/<int:pk>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('products/<slug:slug>/reply/<int:pk>/delete/', views.DeleteReplyView.as_view(), name='delete_reply'),
]
