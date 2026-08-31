from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel
from apps.customers.models import Customer
from apps.products.models import Product


class SaleStatus(models.TextChoices):
    COMPLETED = "COMPLETED", "Завершена"
    CANCELLED = "CANCELLED", "Отменена"
    PARTIALLY_RETURNED = "PARTIALLY_RETURNED", "Частичный возврат"
    RETURNED = "RETURNED", "Возвращена"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Наличные"
    CARD = "card", "Карта"
    TRANSFER = "transfer", "Перевод"
    OTHER = "other", "Другое"


class Sale(TimeStampedModel):
    number = models.CharField(max_length=40, unique=True, blank=True)
    status = models.CharField(max_length=30, choices=SaleStatus.choices, default=SaleStatus.COMPLETED, db_index=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="sales")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.PROTECT, related_name="sales")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    comment = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="cancelled_sales")
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "销售单 / Продажа"
        verbose_name_plural = "销售单 / Продажи"
        permissions = [
            ("cancel_sale", "Can cancel sale"),
            ("correct_sale", "Can correct historical sale"),
            ("view_profit", "Can view sale gross profit"),
            ("view_cost_price", "Can view sale cost price"),
        ]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["operator"]),
            models.Index(fields=["completed_at", "status"]),
        ]

    def __str__(self) -> str:
        return self.number


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=80)
    product_size = models.CharField(max_length=80, blank=True)
    product_unit = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, validators=[MinValueValidator(0)])
    returned_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=14, decimal_places=2)
    regular_sale_price = models.DecimalField(max_digits=14, decimal_places=2)
    actual_unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    line_cost = models.DecimalField(max_digits=14, decimal_places=2)
    line_profit = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "销售明细 / Строка продажи"
        verbose_name_plural = "销售明细 / Строки продажи"
        indexes = [models.Index(fields=["product"]), models.Index(fields=["sale", "product"])]
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name="sale_item_quantity_gt_0"),
            models.CheckConstraint(condition=models.Q(actual_unit_price__gte=0), name="sale_item_actual_price_gte_0"),
        ]

    @property
    def returnable_quantity(self):
        return self.quantity - self.returned_quantity

    def __str__(self) -> str:
        return f"{self.product_sku} x {self.quantity}"


class SaleReturn(TimeStampedModel):
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="returns")
    number = models.CharField(max_length=40, unique=True, blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    profit_delta = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reason = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "退货单 / Возврат"
        verbose_name_plural = "退货单 / Возвраты"

    def __str__(self) -> str:
        return self.number


class SaleReturnItem(models.Model):
    sale_return = models.ForeignKey(SaleReturn, on_delete=models.CASCADE, related_name="items")
    sale_item = models.ForeignKey(SaleItem, on_delete=models.PROTECT, related_name="return_items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, validators=[MinValueValidator(0)])
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    line_cost = models.DecimalField(max_digits=14, decimal_places=2)
    line_profit = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0), name="sale_return_item_quantity_gt_0")]


class IdempotencyKey(TimeStampedModel):
    key = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    request_hash = models.CharField(max_length=64)
    response_data = models.JSONField(default=dict, blank=True)
    status_code = models.PositiveSmallIntegerField(default=201)

    class Meta:
        verbose_name = "防重复请求 / Idempotency Key"
        verbose_name_plural = "防重复请求 / Idempotency Keys"
