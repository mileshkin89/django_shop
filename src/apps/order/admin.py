from django.contrib import admin

from .models import Order, OrderItem, Inventory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product", "inventory")
    raw_id_fields = ()  # product, inventory via autocomplete


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "reserve_expires_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("user__email", "reserve_token")
    readonly_fields = ("reserve_token", "reserve_expires_at", "created_at", "updated_at")
    raw_id_fields = ("user", "token", "shipping_address")
    inlines = (OrderItemInline,)
    date_hierarchy = "updated_at"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "inventory", "quantity", "get_total_price_items_display")
    list_filter = ("order__status",)
    search_fields = ("order__user__email", "product__product_display_name")
    autocomplete_fields = ("product", "inventory")
    raw_id_fields = ("order",)

    def get_total_price_items_display(self, obj):
        return obj.get_total_price_items

    get_total_price_items_display.short_description = "Сумма"


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "stock", "reserved", "price", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("product__product_display_name",)
    raw_id_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "updated_at"
