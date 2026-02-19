from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("forgot_pass/", views.PasswordResetRequestView.as_view(), name="forgot-password"),
    path("reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("reset/complete/", views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("account/", views.OrderHistoryView.as_view(), name="order_history"),
    path("update_account/", views.UserUpdateAccountView.as_view(), name="update_account"),
    path("change_password/", views.PasswordChangeView.as_view(), name="change_password"),
]
