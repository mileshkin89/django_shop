from apps.catalog.models import MasterCategory, SubCategory, ArticleType
from django.db.models import Prefetch


def categories(request):
    sub_queryset = SubCategory.objects.order_by("name").prefetch_related(
        Prefetch(
            "article_types",
            queryset=ArticleType.objects.order_by("name"),
        )
    )

    master_queryset = (
        MasterCategory.objects
        .order_by("name")
        .prefetch_related(Prefetch("sub_categories", queryset=sub_queryset))
    )

    return {
        "nav_categories": master_queryset
    }
