from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.purchases.models import ReceiptStatus, StockReceipt, StockReceiptItem


class StockReceiptItemInline(TabularInline):
    model = StockReceiptItem
    autocomplete_fields = ["product"]
    extra = 1
    readonly_fields = ["line_total"]


@admin.register(StockReceipt)
class StockReceiptAdmin(ModelAdmin):
    list_display = ["number", "date", "supplier", "status", "total", "created_by", "created_at"]
    list_filter = ["status", "date", "supplier"]
    search_fields = ["number", "supplier__name", "comment"]
    readonly_fields = ["number", "status", "total", "posted_at", "cancelled_at", "cancel_reason", "created_at", "updated_at"]
    autocomplete_fields = ["supplier"]
    inlines = [StockReceiptItemInline]

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status != ReceiptStatus.DRAFT:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
