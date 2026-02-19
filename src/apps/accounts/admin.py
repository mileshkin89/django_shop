from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, ShippingAddress


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0
    verbose_name = "адрес доставки"
    verbose_name_plural = "адреса доставки"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "is_superuser", "date_joined")
    search_fields = ("email", "username", "first_name", "last_name", "phone_number")
    ordering = ("-date_joined",)
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личные данные", {"fields": ("username", "first_name", "last_name", "phone_number")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Группы и права", {"fields": ("groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )

    inlines = (ShippingAddressInline,)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "shipping_address")
    list_filter = ("user",)
    search_fields = ("user__email", "shipping_address")
    raw_id_fields = ("user",)
    ordering = ("user", "shipping_address")
