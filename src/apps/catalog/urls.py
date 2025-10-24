from django.urls import path
from . import views
from .views import load_subcategories, load_article_types

app_name = "catalog"

urlpatterns = [

    path(
        "products/category/<slug:master_slug>/",
        views.ProductByMasterCategoryListView.as_view(),
        name="product_list_by_master"),
    path(
        "products/category/<slug:master_slug>/<slug:sub_slug>/",
        views.ProductBySubCategoryListView.as_view(),
        name="product_list_by_sub"),
    path(
        "products/category/<slug:master_slug>/<slug:sub_slug>/<slug:article_slug>/",
        views.ProductByArticleTypeListView.as_view(),
        name="product_list_by_article"),

    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    path('api/load-subcategories/', load_subcategories, name='api_load_subcategories'),
    path('api/load-article-types/', load_article_types, name='api_load_article_types'),

    path('', views.HomePageViev.as_view(), name='home'),
]
