import json
import logging

import stripe
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from .models import Order, OrderItem, Inventory
from .stripe_service import create_checkout_session, handle_checkout_completed
from apps.catalog.models import Product
from apps.accounts.models import ShippingAddress
from .reserve_cleaner.decorator import clear_expired_reserves

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator(clear_expired_reserves, name='dispatch')
class OrderItemView(View):
    def get(self, request):
        order = getattr(request, 'order', None)

        if not order:
            return JsonResponse({'quantity': 0, 'price': 0})

        slug = request.GET.get('slug')
        if not slug:
            return JsonResponse({'error': 'Missing slug'}, status=400)

        product = get_object_or_404(Product, slug=slug)

        order_item = order.order_items.filter(product=product).first()
        total_price = float(order.total_price)

        if order_item:
            return JsonResponse({
                'quantity': order_item.quantity,
                'price': order_item.inventory.price,
                'status': order.status,
                'total_price': total_price,
            })
        return JsonResponse({'quantity': 0, 'price': 0})

    def post(self, request, *args, **kwargs):
        order = getattr(request, 'order', None)

        if not order:
            return JsonResponse({'error': 'No active cart found.'}, status=404)

        data = request.POST or request.body
        if isinstance(data, bytes):
            data = json.loads(data.decode('utf-8'))

        slug = data.get('slug')
        quantity = int(data.get('quantity', 1))
        product = get_object_or_404(Product, slug=slug)

        inventory = Inventory.objects.filter(product=product).first()
        if not inventory:
            return JsonResponse({'error': 'No inventory for this product.'}, status=400)

        # Send a message to the client
        if quantity > inventory.stock:
            return JsonResponse({'error': 'Not enough stock for this product.'}, status=400)

        with transaction.atomic():
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                inventory=inventory,
                defaults={'quantity': quantity}
            )

            if not created:
                order_item.quantity = quantity
                order_item.save()

            if order_item.quantity == 0:
                order_item.delete()

            order.refresh_from_db()

            if order.order_items.exists():
                order.total_price = sum(
                    item.quantity * item.inventory.price for item in order.order_items.all()
                )
                order.save(update_fields=["total_price", "updated_at"])
            else:
                order.delete()

                return JsonResponse({
                    'success': True,
                    'order_id': None,
                    'total_price': 0.00,
                    'item_quantity': 0,
                })

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'total_price': float(order.total_price),
            'item_quantity': order_item.quantity,
        })

    def delete(self, request, *args, **kwargs):
        order = getattr(request, 'order', None)

        if not order:
            return JsonResponse({'error': 'No active cart found.'}, status=404)

        if request.content_type == "application/json":
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = QueryDict(request.body)

        slug = data.get('slug')

        with transaction.atomic():
            order_item = order.order_items.filter(product__slug=slug).first()
            if order_item:
                order_item.delete()

            order.refresh_from_db()

            if not order.order_items.exists():
                order.delete()
                total_price = 0.00
                order_id = None
            else:
                order.total_price = sum(
                    item.quantity * item.inventory.price for item in order.order_items.all()
                )
                order.save(update_fields=["total_price", "updated_at"])
                total_price = float(order.total_price)
                order_id = order.id

        return JsonResponse({
            'success': True,
            'order_id': order_id,
            'total_price': total_price,
        })


@method_decorator(clear_expired_reserves, name='dispatch')
class OrderItemListView(ListView):
    model = OrderItem
    template_name = 'pages/cart/cart.html'
    context_object_name = 'cart_items'

    paginate_by = 10
    PER_PAGE_ALLOWED = {"4", "10", "20"}

    def get_queryset(self):
        order = getattr(self.request, 'order', None)
        if not order:
            return OrderItem.objects.none()
        return OrderItem.objects.filter(order=order).select_related('inventory', 'product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = getattr(self.request, 'order', None)
        context['order'] = order
        return context

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page")
        if per_page in self.PER_PAGE_ALLOWED:
            return int(per_page)
        return self.paginate_by


class CartTotalPriceView(View):
    def get(self, request, *args, **kwargs):
        order = getattr(request, 'order', None)

        if order:
            total_price = float(order.total_price)
        else:
            total_price = 0.00

        return JsonResponse({'success': True, 'total_price': total_price})


class CheckoutStartView(LoginRequiredMixin, View):
    def post(self, request):
        order = getattr(request, 'order', None)

        if not order:
            messages.error(request, "No active cart found.")
            return redirect('order:cart')

        # If the order is already in the "Pending" status, redirect to 'checkout_details'
        if order.status == 'Pending':
            return redirect('order:checkout_details')

        if order.status != 'Cart':
            messages.error(request, "No active cart found.")
            return redirect('order:cart')

        if order.is_empty:
            messages.error(request, "Cart is empty.")
            return redirect('order:cart')

        order.start_checkout()
        return redirect('order:checkout_details')


class CheckoutDetailsView(LoginRequiredMixin, View):
    template_name = 'pages/cart/checkout.html'

    def get(self, request):
        """
        Render the checkout form.
        Ensures there is an active order with status 'Pending'.
        """
        order = getattr(request, 'order', None)

        if not order or order.status != 'Pending':
            messages.error(request, "No active order to proceed with checkout.")
            if order:
                order.checkout_cancel()
            return redirect('order:cart')

        if order.is_empty:
            messages.error(request, "Cart is empty.")
            order.checkout_cancel()
            return redirect('order:cart')

        # Fetch user's existing shipping addresses
        shipping_addresses = ShippingAddress.objects.filter(user=request.user)

        context = {
            'order': order,
            'user': request.user,
            'shipping_addresses': shipping_addresses,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """
        Handle checkout form submission.
        Saves shipping address and updates the user and the order.
        """
        order = getattr(request, 'order', None)

        if not order or order.status != 'Pending':
            messages.error(request, "No active order to proceed with checkout.")
            return redirect('order:cart')

        if order.is_empty:
            messages.error(request, "Cart is empty.")
            order.checkout_cancel()
            return redirect('order:cart')

        first_name = request.POST.get("first_name")
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        if not all([first_name, last_name, phone, email, address]):
            messages.error(request, "Please fill in all fields.")
            shipping_addresses = ShippingAddress.objects.filter(user=request.user)
            return render(request, self.template_name, {
                'order': order,
                'user': request.user,
                'shipping_addresses': shipping_addresses,
            })

        user = request.user

        # Validate email uniqueness for other users
        if email != user.email:
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, "This email is already used by another user.")
                shipping_addresses = ShippingAddress.objects.filter(user=request.user)
                return render(request, self.template_name, {
                    'order': order,
                    'user': request.user,
                    'shipping_addresses': shipping_addresses,
                })

        # Validate phone number uniqueness for other users
        if phone and (not user.phone_number or phone != user.phone_number):
            if User.objects.filter(phone_number=phone).exclude(pk=user.pk).exists():
                messages.error(request, "This phone number is already used by another user.")
                shipping_addresses = ShippingAddress.objects.filter(user=request.user)
                return render(request, self.template_name, {
                    'order': order,
                    'user': request.user,
                    'shipping_addresses': shipping_addresses,
                })

        try:
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone
            user.email = email
            user.save(update_fields=['first_name', 'last_name', 'phone_number', 'email'])
        except IntegrityError:
            messages.error(request, "Error saving data. The email or phone number may already be in use.")
            shipping_addresses = ShippingAddress.objects.filter(user=request.user)
            return render(request, self.template_name, {
                'order': order,
                'user': request.user,
                'shipping_addresses': shipping_addresses,
            })

        shipping_address, _ = ShippingAddress.objects.get_or_create(
            user=user,
            shipping_address=address,
        )

        order.shipping_address = shipping_address
        order.updated_at = timezone.now()
        order.save(update_fields=['shipping_address', 'updated_at'])

        success_url = request.build_absolute_uri('/checkout/success/?session_id={CHECKOUT_SESSION_ID}')
        cancel_url = request.build_absolute_uri('/checkout/cancel/')

        try:
            stripe_url = create_checkout_session(order, success_url, cancel_url)
        except stripe.StripeError:
            logger.exception("Stripe session creation failed for order %s", order.id)
            messages.error(request, "Payment service is temporarily unavailable. Please try again.")
            return redirect('order:checkout_details')

        return redirect(stripe_url)


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/cart/checkout_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.request.GET.get("session_id")
        if session_id:
            order = Order.objects.filter(stripe_session_id=session_id).first()
            context["order"] = order
        return context


class CheckoutCancelView(LoginRequiredMixin, View):
    def get(self, request):
        order = getattr(request, 'order', None)

        if order and order.status == 'Pending':
            order.stripe_session_id = None
            order.save(update_fields=["stripe_session_id", "updated_at"])
            order.checkout_cancel()

        messages.info(request, "Payment was cancelled.")
        return redirect('order:cart')


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, django_settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            logger.warning("Invalid Stripe webhook payload")
            return HttpResponse(status=400)
        except stripe.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            handle_checkout_completed(event["data"]["object"])

        return HttpResponse(status=200)
