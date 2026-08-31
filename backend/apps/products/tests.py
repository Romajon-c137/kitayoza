from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.products.models import Category, Product


@pytest.mark.django_db
def test_product_sku_is_unique():
    category = Category.objects.create(name="Смесители", slug="smesiteli")
    Product.objects.create(sku="MIX-001", name="Смеситель", category=category, cost_price=Decimal("10"), sale_price=Decimal("20"))
    with pytest.raises(IntegrityError):
        Product.objects.create(sku="MIX-001", name="Другой", category=category, cost_price=Decimal("10"), sale_price=Decimal("20"))
