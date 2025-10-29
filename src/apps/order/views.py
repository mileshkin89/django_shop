from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views import View
from django.contrib.auth import get_user_model
import json

from django.views.generic import ListView
from django.http import QueryDict

from .models import Order, OrderItem, Inventory
from apps.catalog.models import Product


User = get_user_model()

class OrderItemView(View):
    def get(self, request):
        """
        Checking if there is an item in the cart and how much there is.
        """
        if request.user.is_authenticated:
            user = request.user
        else:
            anonim_user = User.objects.get(id=201)
            user = anonim_user

        slug = request.GET.get('slug')
        if not slug:
            return JsonResponse({'error': 'Missing slug'}, status=400)

        status = request.GET.get('status')
        if not status:
            status = "Cart"

        product = get_object_or_404(Product, slug=slug)

        order = (
            Order.objects.filter(user=user, status=status)
            .prefetch_related('order_items')
            .first()
        )

        if not order:
            return JsonResponse({'quantity': 0, 'price': 0})

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
        if request.user.is_authenticated:
            address = request.user.shipping_address.first()
            user = request.user
        else:
            anonim_user = User.objects.get(id=201)
            address = anonim_user.shipping_address.first()
            user = anonim_user

        data = request.POST or request.body
        if isinstance(data, bytes):
            data = json.loads(data.decode('utf-8'))

        slug = data.get('slug')
        quantity = int(data.get('quantity', 1))
        product = get_object_or_404(Product, slug=slug)

        inventory = Inventory.objects.filter(product=product).first()
        if not inventory:
            return JsonResponse({'error': 'No inventory for this product.'}, status=400)

        with transaction.atomic():
            order, _ = Order.objects.get_or_create(
                user=user,
                status="Cart",
                defaults={'shipping_address': address}
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
                item.quantity * item.inventory.price for item in order.order_items.all()
            )
            order.save()

        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'total_price': float(order.total_price),
            'item_quantity': order_item.quantity,
        })

    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            anonim_user = User.objects.get(id=201)
            user = anonim_user

        order = (
            Order.objects.filter(user=user, status="Cart")
            .prefetch_related('order_items')
            .first()
        )

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

            if not order.order_items.exists():
                order.delete()
                total_price = 0.00
                order_id = None
            else:
                order.total_price = sum(
                    item.quantity * item.inventory.price for item in order.order_items.all()
                )
                order.save()
                total_price = float(order.total_price)
                order_id = order.id

        return JsonResponse({
            'success': True,
            'order_id': order_id,
            'total_price': total_price,
        })


class OrderItemListView(ListView):
    model = OrderItem
    template_name = 'pages/cart/cart.html'
    context_object_name = 'cart_items'

    paginate_by = 10
    PER_PAGE_ALLOWED = {"4", "10", "20"}

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page")
        if per_page in self.PER_PAGE_ALLOWED:
            return int(per_page)
        return self.paginate_by


class CartTotalPriceView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            anonim_user = User.objects.get(id=201)
            user = anonim_user

        order = Order.objects.filter(user=user, status="Cart").first()

        if order:
            total_price = float(order.total_price)
        else:
            total_price = 0.00

        return JsonResponse({'success': True, 'total_price': total_price})