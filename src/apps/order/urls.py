from django.urls import path
from . import views


app_name = "order"

urlpatterns = [
    path('cart/cart_item/', views.OrderItemView.as_view(), name='cart_item_add_edit_del'),
    path('cart/total/', views.CartTotalPriceView.as_view(), name='cart_total_price'),
    path('cart/', views.OrderItemListView.as_view(), name='cart'),

    path('checkout/start/', views.CheckoutStartView.as_view(), name='checkout_start'),
    path('checkout/details/', views.CheckoutDetailsView.as_view(), name='checkout_details'),
    path('checkout/success/', views.CheckoutSuccessView.as_view(), name='checkout_success'),
    path('checkout/cancel/', views.CheckoutCancelView.as_view(), name='checkout_cancel'),
    path('checkout/webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
]