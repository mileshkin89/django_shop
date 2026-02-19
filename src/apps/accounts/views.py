from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView as AuthPasswordResetView,
    PasswordResetDoneView as AuthPasswordResetDoneView,
    PasswordResetConfirmView as AuthPasswordResetConfirmView,
    PasswordResetCompleteView as AuthPasswordResetCompleteView,
)
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import (
    CustomAuthenticationForm,
    UserRegistrationForm,
    UserAccountForm,
    PasswordChangeForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
)
from .models import User
from apps.order.models import Order
from apps.order.utils import merge_guest_cart_to_user_cart, get_guest_cart_from_token
from apps.order.cookies import OrderCookieManager
from apps.order.reserve_cleaner.decorator import clear_expired_reserves


class UserLoginView(LoginView):
    template_name = 'pages/accounts/login.html'
    authentication_form = CustomAuthenticationForm
    
    def form_valid(self, form):
        # Read guest cart token from cookie before authentication
        guest_token = OrderCookieManager.get_token(self.request)
        guest_order = None
        
        if guest_token:
            guest_order = get_guest_cart_from_token(guest_token)
        
        # Authenticate user
        response = super().form_valid(form)
        
        # After successful login, merge guest cart (if exists) into user cart
        if guest_order and self.request.user.is_authenticated:
            merged_order = merge_guest_cart_to_user_cart(guest_order, self.request.user)
            if merged_order:
                # Clear guest cart cookie after successful merge
                OrderCookieManager.clear_token(response)

        return response


class UserLogoutView(LogoutView):
    next_page = 'catalog:home'


class UserRegistrationView(CreateView):
    template_name = 'pages/accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')


@method_decorator(clear_expired_reserves, name='dispatch')
class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'pages/accounts/account.html'
    context_object_name = 'order_history'

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-created_at')


class UserUpdateAccountView(LoginRequiredMixin, UpdateView):
    template_name = 'pages/accounts/account.html'
    form_class = UserAccountForm
    model = User
    success_url = reverse_lazy('accounts:update_account')

    def get_object(self, queryset=None):
        return self.request.user


class PasswordChangeView(LoginRequiredMixin, FormView):
    """View for authenticated user to change password."""

    template_name = "pages/accounts/change_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("accounts:change_password")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)


class PasswordResetRequestView(AuthPasswordResetView):
    """Request password reset: user enters email, receives reset link by email."""

    template_name = "pages/accounts/forgot_password.html"
    form_class = PasswordResetRequestForm
    email_template_name = "pages/accounts/emails/password_reset_email.html"
    subject_template_name = "pages/accounts/emails/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(AuthPasswordResetDoneView):
    """Shown after reset email has been sent (no link disclosure)."""

    template_name = "pages/accounts/password_reset_done.html"


class PasswordResetConfirmView(AuthPasswordResetConfirmView):
    """Set new password from link (uidb64 + token)."""

    template_name = "pages/accounts/password_reset_confirm.html"
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(AuthPasswordResetCompleteView):
    """Shown after password has been successfully reset."""

    template_name = "pages/accounts/password_reset_complete.html"