from django.db.models import Prefetch, Q
from django.utils.http import urlencode
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Product, MasterCategory, SubCategory, ArticleType
from django.urls import reverse_lazy, reverse


class HomePageViev(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["breadcrumbs"] = [
            ("Home", None),
        ]


class ProductListView(ListView):
    model = Product
    template_name = 'pages/catalog/product_list.html'
    context_object_name = 'products'

    paginate_by = 16
    PER_PAGE_ALLOWED = {"12", "16", "20", "24"}

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get("per_page")
        if per_page in self.PER_PAGE_ALLOWED:
            return int(per_page)
        return self.paginate_by

    def _get_base_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "article_type",
                "article_type__sub_category",
                "article_type__sub_category__master_category",
                "base_colour",
                "season",
                "usage_type",
            )
        )

    def apply_category_filters_queryset(self, queryset):
        return queryset

    def get_options_scope_queryset(self):
        queryset = self._get_base_queryset()
        return self.apply_category_filters_queryset(queryset)

    def get_queryset(self):
        queryset = self._get_base_queryset()

        queryset = self.apply_category_filters_queryset(queryset)

        gender_param = self.request.GET.get("gender")
        if gender_param:
            genders = [g.strip() for g in gender_param.split(",") if g.strip()]
            if genders:
                queryset = queryset.filter(gender__in=genders)

        season_param = self.request.GET.get("season")
        if season_param:
            season_slugs = [s.strip() for s in season_param.split(",") if s.strip()]
            if season_slugs:
                queryset = queryset.filter(season__slug__in=season_slugs)

        ordering = self.request.GET.get("ordering")
        ordering_map = {
            "name_asc": ("product_display_name", "pk"),
            "name_desc": ("-product_display_name", "-pk"),
            "year_desc": ("-year", "-pk"),
            "year_asc": ("year", "pk"),
            "created_desc": ("-created_at", "-pk"),
            "created_asc": ("created_at", "pk"),
        }
        if ordering in ordering_map:
            queryset = queryset.order_by(*ordering_map[ordering])

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_query'] = self.request.GET.get('q', '')

        context["current_order"] = self.request.GET.get("ordering", "")

        per_page = self.request.GET.get("per_page")
        context["current_per_page"] = per_page if per_page in self.PER_PAGE_ALLOWED else ""

        gender_param = self.request.GET.get("gender", "")
        selected_genders = [g.strip() for g in gender_param.split(",") if g.strip()]
        context["selected_genders"] = selected_genders

        season_param = self.request.GET.get("season", "")
        selected_seasons = [s.strip() for s in season_param.split(",") if s.strip()]
        context["selected_seasons"] = selected_seasons

        scope_queryset = self.get_options_scope_queryset()

        context["gender_options"] = list(
            scope_queryset.values_list("gender", flat=True).distinct().order_by("gender")
        )

        context["season_options"] = list(
            scope_queryset.values_list("season__name", "season__slug").distinct().order_by("season__name")
        )

        params = self.request.GET.copy()
        params.pop("page", None)
        filter_query_string = urlencode(params, doseq=True)
        context["filter_query_string"] = f"&{filter_query_string}" if filter_query_string else ""

        context["master_categories"] = MasterCategory.objects.order_by("name")

        context["breadcrumbs"] = [
            ("Home", reverse("catalog:home")),
            ("Catalog", None),
        ]
        return context


class ProductSearchListView(ProductListView):

    def get_queryset(self):
        queryset = super().get_queryset()

        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(product_display_name__icontains=query) # | Q(description__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_query'] = self.request.GET.get('q', '')
        return context



class ProductByMasterCategoryListView(ProductListView):

    def apply_category_filters_queryset(self, queryset):
        master_slug = self.kwargs.get("master_slug")
        return queryset.filter(article_type__sub_category__master_category__slug=master_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        master_slug = self.kwargs.get("master_slug")
        context["master_category"] = get_object_or_404(
            MasterCategory.objects.prefetch_related(
                Prefetch("sub_categories", queryset=SubCategory.objects.order_by("name"))
            ),
            slug=master_slug,
        )

        master = context["master_category"]
        context["breadcrumbs"] = [
            ("Home", reverse("catalog:home")),
            (master.name, None),
        ]
        return context


class ProductBySubCategoryListView(ProductListView):

    def apply_category_filters_queryset(self, queryset):
        master_slug = self.kwargs.get("master_slug")
        sub_slug = self.kwargs.get("sub_slug")
        return queryset.filter(
            article_type__sub_category__master_category__slug=master_slug,
            article_type__sub_category__slug=sub_slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        master_slug = self.kwargs.get("master_slug")
        sub_slug = self.kwargs.get("sub_slug")
        master = get_object_or_404(
            MasterCategory.objects.prefetch_related(
                Prefetch("sub_categories", queryset=SubCategory.objects.order_by("name"))
            ),
            slug=master_slug,
        )
        sub = get_object_or_404(
            SubCategory.objects.prefetch_related(
                Prefetch("article_types", queryset=ArticleType.objects.order_by("name"))
            ),
            slug=sub_slug,
            master_category=master,
        )
        context["master_category"] = master
        context["sub_category"] = sub

        context["breadcrumbs"] = [
            ("Home", reverse("catalog:home")),
            (master.name, reverse("catalog:product_list_by_master", args=[master.slug])),
            (sub.name, None),
        ]
        return context


class ProductByArticleTypeListView(ProductListView):

    def apply_category_filters_queryset(self, queryset):
        master_slug = self.kwargs.get("master_slug")
        sub_slug = self.kwargs.get("sub_slug")
        article_slug = self.kwargs.get("article_slug")
        return queryset.filter(
            article_type__sub_category__master_category__slug=master_slug,
            article_type__sub_category__slug=sub_slug,
            article_type__slug=article_slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        master_slug = self.kwargs.get("master_slug")
        sub_slug = self.kwargs.get("sub_slug")
        article_slug = self.kwargs.get("article_slug")

        master = get_object_or_404(
            MasterCategory.objects.prefetch_related(
                Prefetch("sub_categories", queryset=SubCategory.objects.order_by("name"))
            ),
            slug=master_slug,
        )
        sub = get_object_or_404(
            SubCategory.objects.prefetch_related(
                Prefetch("article_types", queryset=ArticleType.objects.order_by("name"))
            ),
            slug=sub_slug,
            master_category=master,
        )
        article = get_object_or_404(ArticleType, slug=article_slug, sub_category=sub)

        context["master_category"] = master
        context["sub_category"] = sub
        context["article_type"] = article

        context["breadcrumbs"] = [
            ("Home", reverse("catalog:home")),
            (master.name, reverse("catalog:product_list_by_master", args=[master.slug])),
            (sub.name, reverse("catalog:product_list_by_sub", args=[master.slug, sub.slug])),
            (article.name, None),
        ]
        return context



class ProductDetailView(DetailView):
    model = Product
    template_name = 'pages/catalog/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        master = product.article_type.sub_category.master_category
        sub = product.article_type.sub_category
        article = product.article_type

        context["breadcrumbs"] = [
            ("Home", reverse("catalog:home")),
            (master.name, reverse("catalog:product_list_by_master", args=[master.slug])),
            (sub.name, reverse("catalog:product_list_by_sub", args=[master.slug, sub.slug])),
            (article.name, reverse("catalog:product_list_by_article", args=[master.slug, sub.slug, article.slug])),
            (product.product_display_name, None),
        ]
        return context



class ProductCreateView(CreateView):
    model = Product
    fields = ['product_display_name', 'gender', 'season']
    template_name = 'pages/catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_detail')

    def get_success_url(self):
        return reverse_lazy(
            "catalog:product_detail",
            kwargs={"slug": self.object.slug}
        )


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['product_display_name', 'gender', 'season']
    template_name = 'pages/catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_detail')

    def get_success_url(self):
        return reverse_lazy(
            "catalog:product_detail",
            kwargs={"slug": self.object.slug}
        )


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'pages/catalog/product_delete.html'
    success_url = reverse_lazy('catalog:product_list')
