from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class ProductUnit(models.TextChoices):
    PCS = "pcs", "шт."
    M2 = "m2", "м2"
    METER = "meter", "м"
    BOX = "box", "коробка"
    SET = "set", "комплект"


class Category(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "分类 / Категория"
        verbose_name_plural = "分类 / Категории"
        indexes = [models.Index(fields=["name"]), models.Index(fields=["slug"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    sku = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.PROTECT, related_name="products")
    brand = models.CharField(max_length=120, blank=True)
    model = models.CharField(max_length=120, blank=True)
    size = models.CharField(max_length=80, blank=True)
    color = models.CharField(max_length=80, blank=True)
    unit = models.CharField(max_length=20, choices=ProductUnit.choices, default=ProductUnit.PCS)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    current_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0, validators=[MinValueValidator(0)])
    minimum_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "商品 / Товар"
        verbose_name_plural = "商品 / Товары"
        permissions = [
            ("view_cost_price", "Can view cost price"),
            ("view_profit", "Can view gross profit"),
        ]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["name"]),
            models.Index(fields=["brand", "model"]),
            models.Index(fields=["is_active", "current_stock"]),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(cost_price__gte=0), name="product_cost_price_gte_0"),
            models.CheckConstraint(condition=models.Q(sale_price__gte=0), name="product_sale_price_gte_0"),
            models.CheckConstraint(condition=models.Q(current_stock__gte=0), name="product_current_stock_gte_0"),
        ]

    @property
    def expected_unit_profit(self):
        return self.sale_price - self.cost_price

    def __str__(self) -> str:
        return f"{self.sku} - {self.name}"
