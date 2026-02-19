from django.contrib import admin

from .models import (
    MasterCategory,
    SubCategory,
    ArticleType,
    BaseColour,
    Season,
    UsageType,
    Product,
)


class SubCategoryInline(admin.StackedInline):
    model = SubCategory
    extra = 0
    show_change_link = True


@admin.register(MasterCategory)
class MasterCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (SubCategoryInline,)


class ArticleTypeInline(admin.StackedInline):
    model = ArticleType
    extra = 0
    show_change_link = True


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "master_category", "slug")
    list_filter = ("master_category",)
    search_fields = ("name", "master_category__name")
    autocomplete_fields = ("master_category",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (ArticleTypeInline,)


@admin.register(ArticleType)
class ArticleTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "sub_category", "slug")
    list_filter = ("sub_category__master_category", "sub_category")
    search_fields = ("name", "sub_category__name")
    autocomplete_fields = ("sub_category",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BaseColour)
class BaseColourAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(UsageType)
class UsageTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_display_name",
        "product_id",
        "article_type",
        "base_colour",
        "gender",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active", "gender", "article_type", "base_colour", "season", "usage_type")
    search_fields = ("product_display_name", "description", "product_id")
    list_editable = ("is_active",)
    autocomplete_fields = ("article_type", "base_colour", "season", "usage_type")
    readonly_fields = ("slug", "created_at", "updated_at")
    date_hierarchy = "updated_at"
