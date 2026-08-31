from django.db import models

from apps.core.models import TimeStampedModel


class Customer(TimeStampedModel):
    name = models.CharField(max_length=180)
    phone = models.CharField(max_length=50, blank=True)
    company_name = models.CharField(max_length=180, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = "客户 / Клиент"
        verbose_name_plural = "客户 / Клиенты"
        indexes = [models.Index(fields=["name"]), models.Index(fields=["phone"])]

    def __str__(self) -> str:
        return self.company_name or self.name
