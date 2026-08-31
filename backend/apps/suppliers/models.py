from django.db import models

from apps.core.models import TimeStampedModel


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=180)
    phone = models.CharField(max_length=50, blank=True)
    contact_person = models.CharField(max_length=120, blank=True)
    comment = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "供应商 / Поставщик"
        verbose_name_plural = "供应商 / Поставщики"
        indexes = [models.Index(fields=["name"]), models.Index(fields=["is_active"])]

    def __str__(self) -> str:
        return self.name
