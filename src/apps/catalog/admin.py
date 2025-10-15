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
# admin_Pass123

# Register your models here.
admin.site.register(MasterCategory)
admin.site.register(SubCategory)
admin.site.register(ArticleType)
admin.site.register(BaseColour)
admin.site.register(Season)
admin.site.register(UsageType)

admin.site.register(Product)