from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.audit.models import AuditAction, AuditLog
from apps.inventory.models import InventoryMovement, InventoryMovementType
from apps.inventory.services import adjust_stock
from apps.products.models import Category, Product, ProductUnit
from apps.purchases.models import StockReceipt, StockReceiptItem
from apps.purchases.services import post_receipt
from apps.sales.models import SaleItem, SaleStatus
from apps.sales.services import complete_sale, correct_sale, create_sale_return

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username="operator", password="pass")


@pytest.fixture
def product():
    category = Category.objects.create(name="Унитазы", slug="unitazy")
    return Product.objects.create(
        sku="WC-MONACO",
        name="Унитаз Monaco",
        category=category,
        unit=ProductUnit.PCS,
        cost_price=Decimal("800.00"),
        sale_price=Decimal("1200.00"),
    )


@pytest.mark.django_db
def test_receipt_increases_stock_and_updates_cost(product, user):
    receipt = StockReceipt.objects.create(date=timezone.localdate(), created_by=user)
    StockReceiptItem.objects.create(receipt=receipt, product=product, quantity=Decimal("10"), cost_price=Decimal("900"))

    post_receipt(receipt_id=receipt.id, user=user)

    product.refresh_from_db()
    receipt.refresh_from_db()
    assert product.current_stock == Decimal("10.000")
    assert product.cost_price == Decimal("900.00")
    assert receipt.total == Decimal("9000.00")
    assert InventoryMovement.objects.filter(product=product, movement_type=InventoryMovementType.RECEIPT).exists()


@pytest.mark.django_db
def test_sale_uses_total_price_and_stores_historical_cost_snapshot(product, user):
    adjust_stock(product_id=product.id, quantity_delta=Decimal("150"), reason="initial", user=user)

    sale = complete_sale(
        payload={"items": [{"product_id": product.id, "quantity": "100", "total_price": "100000"}], "payment_method": "cash"},
        user=user,
        idempotency_key="sale-1",
    )

    product.refresh_from_db()
    item = SaleItem.objects.get(sale=sale)
    assert product.current_stock == Decimal("50.000")
    assert item.cost_price == Decimal("800.00")
    assert item.actual_unit_price == Decimal("1000.00")
    assert item.line_total == Decimal("100000.00")
    assert item.line_cost == Decimal("80000.00")
    assert item.line_profit == Decimal("20000.00")

    product.cost_price = Decimal("900")
    product.save()
    item.refresh_from_db()
    assert item.cost_price == Decimal("800.00")


@pytest.mark.django_db
def test_sale_idempotency_returns_existing_sale_response(product, user):
    adjust_stock(product_id=product.id, quantity_delta=Decimal("1"), reason="initial", user=user)
    payload = {"items": [{"product_id": product.id, "quantity": "1", "unit_price": "1200"}], "payment_method": "cash"}

    first = complete_sale(payload=payload, user=user, idempotency_key="same-click")
    second = complete_sale(payload=payload, user=user, idempotency_key="same-click")

    product.refresh_from_db()
    assert first.number == second["number"]
    assert product.current_stock == Decimal("0.000")


@pytest.mark.django_db
def test_sale_rejects_insufficient_stock(product, user):
    with pytest.raises(Exception) as exc:
        complete_sale(payload={"items": [{"product_id": product.id, "quantity": "25", "unit_price": "1000"}]}, user=user)
    assert "Недостаточно" in str(exc.value)


@pytest.mark.django_db
def test_returns_cannot_exceed_remaining_quantity(product, user):
    adjust_stock(product_id=product.id, quantity_delta=Decimal("10"), reason="initial", user=user)
    sale = complete_sale(payload={"items": [{"product_id": product.id, "quantity": "10", "unit_price": "1000"}]}, user=user)
    sale_item = sale.items.get()

    create_sale_return(sale_id=sale.id, items=[{"sale_item_id": sale_item.id, "quantity": "3"}], reason="return", user=user)
    create_sale_return(sale_id=sale.id, items=[{"sale_item_id": sale_item.id, "quantity": "4"}], reason="return", user=user)

    with pytest.raises(Exception) as exc:
        create_sale_return(sale_id=sale.id, items=[{"sale_item_id": sale_item.id, "quantity": "4"}], reason="return", user=user)
    assert "больше доступного" in str(exc.value)


@pytest.mark.django_db
def test_sale_correction_updates_stock_totals_and_audit(product, user):
    adjust_stock(product_id=product.id, quantity_delta=Decimal("100"), reason="initial", user=user)
    sale = complete_sale(payload={"items": [{"product_id": product.id, "quantity": "10", "unit_price": "1000"}]}, user=user)
    sale_item = sale.items.get()

    corrected = correct_sale(
        sale_id=sale.id,
        items=[{"sale_item_id": sale_item.id, "quantity": "8", "unit_price": "1000"}],
        reason="Ошибка оператора",
        expected_version=sale.version,
        user=user,
    )

    product.refresh_from_db()
    assert product.current_stock == Decimal("92.000")
    assert corrected.total == Decimal("8000.00")
    assert corrected.total_cost == Decimal("6400.00")
    assert corrected.profit == Decimal("1600.00")
    assert AuditLog.objects.filter(action=AuditAction.SALE_CORRECTED, entity_id=str(sale.id)).exists()
