from django.urls import path
from . import views


app_name = "cart"

urlpatterns = [
    path('cart/add/', views.OrderItemCreateUpdateView.as_view(), name='cart_item_add_edit'),
    # path('cart/delete/', views.OrderItemDeleteView.as_view(), name='cart_item_delete'),
    path('cart/', views.OrderItemListView.as_view(), name='cart_items_list'),
]