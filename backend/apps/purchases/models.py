from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel
from apps.products.models import Product
from apps.suppliers.models import Supplier


class ReceiptStatus(models.TextChoices):
    DRAFT = "DRAFT", "Черновик"
    POSTED = "POSTED", "Проведен"
    CANCELLED = "CANCELLED", "Отменен"


class StockReceipt(TimeStampedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.PROTECT, related_name="receipts")
    status = models.CharField(max_length=20, choices=ReceiptStatus.choices, default=ReceiptStatus.DRAFT, db_index=True)
    date = models.DateField()
    comment = models.TextField(blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    posted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "入库单 / Приход"
        verbose_name_plural = "入库单 / Приходы"
        indexes = [models.Index(fields=["status", "date"]), models.Index(fields=["created_at"])]

    def __str__(self) -> str:
        return self.number or f"Приход #{self.pk}"


class StockReceiptItem(models.Model):
    receipt = models.ForeignKey(StockReceipt, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="receipt_items")
    quantity = models.DecimalField(max_digits=14, decimal_places=3, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = "入库明细 / Строка прихода"
        verbose_name_plural = "入库明细 / Строки прихода"
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name="receipt_item_quantity_gt_0"),
            models.CheckConstraint(condition=models.Q(cost_price__gte=0), name="receipt_item_cost_price_gte_0"),
        ]

    def __str__(self) -> str:
        return f"{self.product.sku} x {self.quantity}"
