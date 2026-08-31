from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.inventory.models import InventoryMovement, StockAdjustment


@admin.register(InventoryMovement)
class InventoryMovementAdmin(ModelAdmin):
    list_display = ["created_at", "product", "movement_type", "quantity", "stock_before", "stock_after", "reference_type", "reference_id", "user"]
    list_filter = ["movement_type", "created_at"]
    search_fields = ["product__sku", "product__name", "reference_id", "comment"]
    readonly_fields = [field.name for field in InventoryMovement._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(ModelAdmin):
    list_display = ["created_at", "product", "quantity_delta", "created_by", "reason"]
    list_filter = ["created_at"]
    search_fields = ["product__sku", "product__name", "reason"]
    readonly_fields = ["movement", "created_at", "updated_at"]
