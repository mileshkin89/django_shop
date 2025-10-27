from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views import View
from django.contrib.auth import get_user_model
import json

from django.views.generic import ListView

from .models import Order, OrderItem, Inventory
from apps.catalog.models import Product
from apps.accounts.models import ShippingAddress

User = get_user_model()


class OrderItemCreateUpdateView(View):
    def get(self, request):
        """Проверка, есть ли товар в корзине, и сколько его."""
        # if not request.user.is_authenticated:
            # return JsonResponse({'quantity': 0})  # Анонимным возвращаем 0
        if request.user.is_authenticated:
            user = request.user
        else:
            anonim_user = User.objects.get(id=2001)
            user = anonim_user

        slug = request.GET.get('slug')
        # status = request.GET.get('status')
        if not slug:
            return JsonResponse({'error': 'Missing slug'}, status=400)

        product = get_object_or_404(Product, slug=slug)

        order = (
            Order.objects.filter(user=user, status="Pending")
            .prefetch_related('order_item')
            .first()
        )

        if not order:
            return JsonResponse({'quantity': 0, 'price': 0})

        order_item = order.order_item.filter(product=product).first()

        if order_item:
            return JsonResponse({
                'quantity': order_item.quantity,
                'price': order_item.inventory.price,
                'status': order.status,
            })
        return JsonResponse({'quantity': 0, 'price': 0})


    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            shipping_address = request.user.shipping_address
            user = request.user
        else:
            anonim_user = User.objects.get(id=2001)
            shipping_address = ShippingAddress.objects.create(
                user=anonim_user,
                shipping_address='Test Shipping Address'
            )
            user = anonim_user

        data = request.POST or request.body
        if isinstance(data, bytes):
            data = json.loads(data.decode('utf-8'))

        slug = data.get('slug')
        # status = request.GET.get('status')
        quantity = int(data.get('quantity', 1))

        product = get_object_or_404(Product, slug=slug)
        inventory = Inventory.objects.filter(product=product).first()
        if not inventory:
            return JsonResponse({'error': 'No inventory for this product.'}, status=400)

        with transaction.atomic():
            order, _ = Order.objects.get_or_create(
                user=user,
                status="Pending",
                defaults={'shipping_address': shipping_address}
            )

            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                inventory=inventory,
                defaults={'quantity': quantity}
            )

            if not created:
                order_item.quantity = quantity
                order_item.save()

            order.total_price = sum(
                item.quantity * item.inventory.price for item in order.order_item.all()
            )
            order.save()

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'total_price': float(order.total_price),
            'item_quantity': order_item.quantity,
        })


class OrderItemListView(ListView):
    model = OrderItem
    template_name = 'pages/cart/cart.html'
    context_object_name = 'order_items'

    paginate_by = 10
    PER_PAGE_ALLOWED = {"4", "10", "20"}

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page")
        if per_page in self.PER_PAGE_ALLOWED:
            return int(per_page)
        return self.paginate_by