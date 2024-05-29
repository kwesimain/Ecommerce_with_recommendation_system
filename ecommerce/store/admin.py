# store/admin.py

from django.contrib import admin
from .models import (
    Category, Product, Customer, Order, OrderItem, 
    UserProfile, UserInteraction, ShippingAddress
)

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'description')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_ordered', 'complete', 'total')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('customer__user__username',)
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity')
    search_fields = ('product__name', 'order__id')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    filter_horizontal = ('recommended_products',)

class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'interaction_type', 'timestamp')
    list_filter = ('interaction_type', 'timestamp')
    search_fields = ('user__username', 'product__name', 'interaction_type')

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order', 'address', 'city', 'region', 'gps', 'date_added')
    search_fields = ('customer__user__username', 'order__id', 'address', 'city', 'state', 'zipcode')
    list_filter = ('city', 'region', 'date_added')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserInteraction, UserInteractionAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
