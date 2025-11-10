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

            order.refresh_from_db() # Add this line to refresh the order instance

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

            order.refresh_from_db() # Add this line to refresh the order instance

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