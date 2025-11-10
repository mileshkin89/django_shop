from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('forgot_pass/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('account/', views.OrderHistoryView.as_view(), name='order_history'),
    path('update_account/', views.UserUpdateAccountView.as_view(), name='update_account'),
]
