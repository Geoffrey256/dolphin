from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price",
                    "discount_percent", "stock", "created_at")
    list_filter = ("category", "discount_percent")
    search_fields = ("name", "brief", "description")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
