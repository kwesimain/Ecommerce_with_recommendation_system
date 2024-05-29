# store/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('process_order/', views.process_order, name='process_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('confirm_payment/<int:order_id>/', views.confirm_payment, name='confirm_payment'),
    path('order_success/', views.order_success, name='order_success'),
    path('order_history/', views.order_history, name='order_history'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
]