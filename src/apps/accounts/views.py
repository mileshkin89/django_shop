from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomAuthenticationForm, UserRegistrationForm, UserAccountForm
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
        if self.request.user.is_authenticated:
            user = self.request.user

        queryset = Order.objects.filter(user=user).all().order_by('-created_at')

        return queryset


class UserUpdateAccountView(LoginRequiredMixin, UpdateView):
    template_name = 'pages/accounts/account.html'
    form_class = UserAccountForm
    model = User
    success_url = reverse_lazy('accounts:update_account')

    def get_object(self, queryset=None):
        return self.request.user


# mock password reset
class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'pages/accounts/forgot_password.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'forgot_password.html')

        new_password = 'new_password123'
        user.set_password(new_password)
        user.save()

        return JsonResponse({
            'success': True,
            'message': "Your password has been reset. An email has been sent with further instructions. (Use 'new_password123' to log in)"
        })