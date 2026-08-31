from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.sales.models import IdempotencyKey, Sale, SaleItem, SaleReturn, SaleReturnItem, SaleStatus


class SaleItemInline(TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = [field.name for field in SaleItem._meta.fields]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Sale)
class SaleAdmin(ModelAdmin):
    list_display = ["number", "completed_at", "operator", "status", "total", "total_cost", "profit", "version"]
    list_filter = ["status", "payment_method", "completed_at", "operator"]
    search_fields = ["number", "items__product_sku", "items__product_name"]
    readonly_fields = [field.name for field in Sale._meta.fields]
    inlines = [SaleItemInline]

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status != SaleStatus.CANCELLED:
            return False
        return False


class SaleReturnItemInline(TabularInline):
    model = SaleReturnItem
    extra = 0
    readonly_fields = [field.name for field in SaleReturnItem._meta.fields]
    can_delete = False


@admin.register(SaleReturn)
class SaleReturnAdmin(ModelAdmin):
    list_display = ["number", "sale", "total", "total_cost", "profit_delta", "created_by", "created_at"]
    search_fields = ["number", "sale__number", "reason"]
    readonly_fields = [field.name for field in SaleReturn._meta.fields]
    inlines = [SaleReturnItemInline]


@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(ModelAdmin):
    list_display = ["key", "user", "status_code", "created_at"]
    readonly_fields = [field.name for field in IdempotencyKey._meta.fields]
