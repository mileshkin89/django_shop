from django.urls import path
from .views import UserLoginView, UserLogoutView, UserRegistrationView, OrderHistoryView, UserUpdateAccountView, \
    ForgotPasswordView

app_name = "accounts"

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('forgot_pass/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('account/', OrderHistoryView.as_view(), name='order_history'),
    path('update_account/', UserUpdateAccountView.as_view(), name='update_account'),
]
