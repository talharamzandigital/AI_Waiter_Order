from django.contrib import admin
from .models import (
    Restaurant, MenuCategory, MenuItem,
    Cart, CartItem, Order, OrderItem, Conversation,
)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    search_fields = ["name", "slug"]

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "display_order"]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["name", "restaurant", "category", "price", "is_available"]
    list_filter = ["is_available", "is_vegetarian"]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "restaurant", "session_key", "status", "created_at"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "restaurant", "status", "payment_status", "total"]

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["session_key", "role", "created_at"]



    # password
    # Admin@123a