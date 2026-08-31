from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel
from apps.products.models import Product


class InventoryMovementType(models.TextChoices):
    INITIAL_BALANCE = "INITIAL_BALANCE", "Начальный остаток"
    RECEIPT = "RECEIPT", "Приход"
    SALE = "SALE", "Продажа"
    SALE_RETURN = "SALE_RETURN", "Возврат покупателя"
    SUPPLIER_RETURN = "SUPPLIER_RETURN", "Возврат поставщику"
    WRITE_OFF = "WRITE_OFF", "Списание"
    ADJUSTMENT_IN = "ADJUSTMENT_IN", "Корректировка плюс"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT", "Корректировка минус"
    SALE_CANCEL = "SALE_CANCEL", "Отмена продажи"
    RECEIPT_CANCEL = "RECEIPT_CANCEL", "Отмена прихода"


class InventoryMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="inventory_movements")
    movement_type = models.CharField(max_length=40, choices=InventoryMovementType.choices, db_index=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    stock_before = models.DecimalField(max_digits=14, decimal_places=3)
    stock_after = models.DecimalField(max_digits=14, decimal_places=3)
    reference_type = models.CharField(max_length=80, blank=True, db_index=True)
    reference_id = models.CharField(max_length=80, blank=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "库存流水 / Движение склада"
        verbose_name_plural = "库存流水 / Движения склада"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["product", "created_at"]), models.Index(fields=["reference_type", "reference_id"])]

    def __str__(self) -> str:
        return f"{self.product.sku} {self.movement_type} {self.quantity}"


class StockAdjustment(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_adjustments")
    quantity_delta = models.DecimalField(max_digits=14, decimal_places=3)
    reason = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    movement = models.OneToOneField(InventoryMovement, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "库存调整 / Корректировка склада"
        verbose_name_plural = "库存调整 / Корректировки склада"
        permissions = [("adjust_stock", "Can adjust stock")]

    def __str__(self) -> str:
        return f"{self.product.sku}: {self.quantity_delta}"
