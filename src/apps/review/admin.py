from django.contrib import admin

from .models import Review, Reply


class ReplyInline(admin.StackedInline):
    model = Reply
    extra = 0
    autocomplete_fields = ("author",)
    verbose_name = "ответ на отзыв"
    verbose_name_plural = "ответы на отзыв"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "author",
        "rating",
        "text_short",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("rating", "is_active", "created_at")
    search_fields = ("text", "author__email", "product__product_display_name")
    autocomplete_fields = ("author", "product")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (ReplyInline,)
    date_hierarchy = "updated_at"

    def text_short(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text

    text_short.short_description = "Текст"


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("review", "author", "text_short", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("text", "author__email", "review__text")
    autocomplete_fields = ("author", "review")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "updated_at"

    def text_short(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text

    text_short.short_description = "Текст"
