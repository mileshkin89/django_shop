from django.urls import path
from . import views


app_name = "order"

urlpatterns = [
    path('cart/cart_item/', views.OrderItemView.as_view(), name='cart_item_add_edit_del'),
    path('cart/total/', views.CartTotalPriceView.as_view(), name='cart_total_price'),
    path('cart/', views.OrderItemListView.as_view(), name='cart'),
]