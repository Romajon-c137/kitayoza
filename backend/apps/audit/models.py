from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    COST_PRICE_CHANGED = "COST_PRICE_CHANGED", "Изменение себестоимости"
    SALE_COMPLETED = "SALE_COMPLETED", "Продажа завершена"
    SALE_CANCELLED = "SALE_CANCELLED", "Продажа отменена"
    SALE_RETURNED = "SALE_RETURNED", "Возврат продажи"
    SALE_CORRECTED = "SALE_CORRECTED", "Исправление продажи"
    RECEIPT_POSTED = "RECEIPT_POSTED", "Приход проведен"
    RECEIPT_CANCELLED = "RECEIPT_CANCELLED", "Приход отменен"
    STOCK_ADJUSTED = "STOCK_ADJUSTED", "Корректировка склада"


class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=60, choices=AuditAction.choices, db_index=True)
    entity_type = models.CharField(max_length=120, db_index=True)
    entity_id = models.CharField(max_length=80, db_index=True)
    old_data = models.JSONField(default=dict, blank=True)
    new_data = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "审计日志 / Audit Log"
        verbose_name_plural = "审计日志 / Audit Logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["entity_type", "entity_id"]), models.Index(fields=["action", "created_at"])]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id}"
