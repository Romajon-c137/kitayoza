from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.products.models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "parent", "is_active"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["thumb", "sku", "name", "category", "unit", "current_stock", "cost_price", "sale_price", "minimum_stock", "is_active"]
    list_filter = ["is_active", "unit", "category"]
    search_fields = ["sku", "name", "brand", "model"]
    readonly_fields = ["current_stock", "expected_unit_profit", "created_at", "updated_at", "thumb"]
    autocomplete_fields = ["category"]
    fieldsets = (
        ("Основное", {"fields": ("sku", "name", "category", "brand", "model", "size", "color", "unit", "description", "image", "thumb")}),
        ("Цена и склад", {"fields": ("cost_price", "sale_price", "expected_unit_profit", "current_stock", "minimum_stock", "is_active")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )

    def thumb(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "Нет фото"

    thumb.short_description = "Фото"
