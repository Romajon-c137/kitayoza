import hashlib
import json
from decimal import Decimal

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import write_audit
from apps.core.decimal import divide_money, money
from apps.core.exceptions import BusinessError
from apps.inventory.models import InventoryMovementType
from apps.inventory.services import apply_stock_movement
from apps.products.models import Product
from apps.sales.models import IdempotencyKey, Sale, SaleItem, SaleReturn, SaleReturnItem, SaleStatus


def _request_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def next_sale_number() -> str:
    year = timezone.localdate().year
    max_id = (Sale.objects.aggregate(value=Max("id"))["value"] or 0) + 1
    return f"SALE-{year}-{max_id:06d}"


def next_return_number() -> str:
    year = timezone.localdate().year
    max_id = (SaleReturn.objects.aggregate(value=Max("id"))["value"] or 0) + 1
    return f"RET-{year}-{max_id:06d}"


def _line_from_product(product: Product, quantity: Decimal, unit_price: Decimal | None, total_price: Decimal | None) -> dict:
    if quantity <= 0:
        raise BusinessError("INVALID_QUANTITY", "Количество должно быть больше нуля.", {"product_id": product.id})
    if total_price is not None and total_price < 0:
        raise BusinessError("INVALID_PRICE", "Сумма строки не может быть отрицательной.", {"product_id": product.id})
    if unit_price is not None and unit_price < 0:
        raise BusinessError("INVALID_PRICE", "Цена не может быть отрицательной.", {"product_id": product.id})
    if total_price is None:
        actual_unit_price = money(unit_price if unit_price is not None else product.sale_price)
        line_total = money(quantity * actual_unit_price)
    else:
        line_total = money(total_price)
        actual_unit_price = divide_money(line_total, quantity)
    line_cost = money(quantity * product.cost_price)
    line_profit = money(line_total - line_cost)
    return {
        "actual_unit_price": actual_unit_price,
        "line_total": line_total,
        "line_cost": line_cost,
        "line_profit": line_profit,
    }


@transaction.atomic
def complete_sale(*, payload: dict, user=None, idempotency_key: str | None = None) -> Sale | dict:
    request_hash = _request_hash(payload)
    idem = None
    if idempotency_key:
        idem, created = IdempotencyKey.objects.select_for_update().get_or_create(
            key=idempotency_key,
            defaults={"user": user if getattr(user, "is_authenticated", False) else None, "request_hash": request_hash},
        )
        if not created:
            if idem.request_hash != request_hash:
                raise BusinessError("IDEMPOTENCY_CONFLICT", "Этот request key уже использован с другим запросом.")
            if idem.response_data:
                return idem.response_data

    items_payload = payload.get("items") or []
    if not items_payload:
        raise BusinessError("EMPTY_SALE", "Добавьте товары в продажу.")

    product_ids = sorted({int(item["product_id"]) for item in items_payload})
    products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(id__in=product_ids)
    }
    if len(products) != len(product_ids):
        raise BusinessError("PRODUCT_NOT_FOUND", "Один из товаров не найден.")

    sale = Sale.objects.create(
        number=next_sale_number(),
        operator=user if getattr(user, "is_authenticated", False) else None,
        customer_id=payload.get("customer_id"),
        payment_method=payload.get("payment_method", "cash"),
        comment=payload.get("comment", ""),
        completed_at=timezone.now(),
    )
    total = Decimal("0")
    total_cost = Decimal("0")

    for item_payload in items_payload:
        product = products[int(item_payload["product_id"])]
        if not product.is_active:
            raise BusinessError("INACTIVE_PRODUCT", "Товар неактивен.", {"product_id": product.id})
        quantity = Decimal(str(item_payload["quantity"]))
        if product.current_stock < quantity:
            raise BusinessError(
                "INSUFFICIENT_STOCK",
                "Недостаточно товара на складе.",
                {"product_id": product.id, "available": str(product.current_stock), "requested": str(quantity)},
            )
        calculated = _line_from_product(
            product,
            quantity,
            Decimal(str(item_payload["unit_price"])) if item_payload.get("unit_price") is not None else None,
            Decimal(str(item_payload["total_price"])) if item_payload.get("total_price") is not None else None,
        )
        SaleItem.objects.create(
            sale=sale,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            product_size=product.size,
            product_unit=product.unit,
            quantity=quantity,
            cost_price=product.cost_price,
            regular_sale_price=product.sale_price,
            **calculated,
        )
        apply_stock_movement(
            product=product,
            movement_type=InventoryMovementType.SALE,
            quantity=quantity,
            user=user,
            reference_type="Sale",
            reference_id=sale.id,
            comment=sale.comment,
        )
        total += calculated["line_total"]
        total_cost += calculated["line_cost"]

    sale.subtotal = money(total)
    sale.total = money(total - sale.discount)
    sale.total_cost = money(total_cost)
    sale.profit = money(sale.total - sale.total_cost)
    sale.save(update_fields=["subtotal", "total", "total_cost", "profit", "updated_at"])
    response_data = {"id": sale.id, "number": sale.number, "total": str(sale.total), "profit": str(sale.profit)}
    if idem:
        idem.response_data = response_data
        idem.save(update_fields=["response_data", "updated_at"])
    write_audit(user=user, action=AuditAction.SALE_COMPLETED, entity_type="Sale", entity_id=sale.id, new_data=response_data)
    return sale


@transaction.atomic
def cancel_sale(*, sale_id: int, reason: str, user=None) -> Sale:
    if not reason.strip():
        raise BusinessError("REASON_REQUIRED", "Укажите причину отмены продажи.")
    sale = Sale.objects.select_for_update().prefetch_related("items").get(id=sale_id)
    if sale.status == SaleStatus.CANCELLED:
        raise BusinessError("SALE_ALREADY_CANCELLED", "Продажа уже отменена.")
    if sale.status in {SaleStatus.PARTIALLY_RETURNED, SaleStatus.RETURNED}:
        raise BusinessError("SALE_HAS_RETURNS", "Нельзя отменить продажу с возвратами.")
    old_data = {"status": sale.status, "total": str(sale.total), "profit": str(sale.profit)}
    for item in sale.items.select_related("product"):
        product = Product.objects.select_for_update().get(id=item.product_id)
        apply_stock_movement(
            product=product,
            movement_type=InventoryMovementType.SALE_CANCEL,
            quantity=item.quantity,
            user=user,
            reference_type="Sale",
            reference_id=sale.id,
            comment=reason,
        )
    sale.status = SaleStatus.CANCELLED
    sale.cancelled_by = user if getattr(user, "is_authenticated", False) else None
    sale.cancelled_at = timezone.now()
    sale.cancel_reason = reason
    sale.version += 1
    sale.save(update_fields=["status", "cancelled_by", "cancelled_at", "cancel_reason", "version", "updated_at"])
    write_audit(
        user=user,
        action=AuditAction.SALE_CANCELLED,
        entity_type="Sale",
        entity_id=sale.id,
        old_data=old_data,
        new_data={"status": sale.status},
        reason=reason,
    )
    return sale


@transaction.atomic
def create_sale_return(*, sale_id: int, items: list[dict], reason: str, user=None) -> SaleReturn:
    if not reason.strip():
        raise BusinessError("REASON_REQUIRED", "Укажите причину возврата.")
    sale = Sale.objects.select_for_update().get(id=sale_id)
    if sale.status == SaleStatus.CANCELLED:
        raise BusinessError("SALE_CANCELLED", "Нельзя вернуть отмененную продажу.")
    sale_items = {item.id: item for item in SaleItem.objects.select_for_update().select_related("product").filter(sale=sale)}
    sale_return = SaleReturn.objects.create(sale=sale, number=next_return_number(), reason=reason, created_by=user)
    total = Decimal("0")
    total_cost = Decimal("0")
    for payload in items:
        sale_item = sale_items.get(int(payload["sale_item_id"]))
        if sale_item is None:
            raise BusinessError("SALE_ITEM_NOT_FOUND", "Строка продажи не найдена.")
        qty = Decimal(str(payload["quantity"]))
        if qty <= 0:
            raise BusinessError("INVALID_QUANTITY", "Количество должно быть больше нуля.")
        if qty > sale_item.returnable_quantity:
            raise BusinessError(
                "RETURN_EXCEEDS_AVAILABLE",
                "Нельзя вернуть больше доступного количества.",
                {"available": str(sale_item.returnable_quantity), "requested": str(qty)},
            )
        line_total = money(qty * sale_item.actual_unit_price)
        line_cost = money(qty * sale_item.cost_price)
        line_profit = money(line_total - line_cost)
        SaleReturnItem.objects.create(
            sale_return=sale_return,
            sale_item=sale_item,
            product=sale_item.product,
            quantity=qty,
            line_total=line_total,
            line_cost=line_cost,
            line_profit=line_profit,
        )
        sale_item.returned_quantity += qty
        sale_item.save(update_fields=["returned_quantity"])
        product = Product.objects.select_for_update().get(id=sale_item.product_id)
        apply_stock_movement(
            product=product,
            movement_type=InventoryMovementType.SALE_RETURN,
            quantity=qty,
            user=user,
            reference_type="SaleReturn",
            reference_id=sale_return.id,
            comment=reason,
        )
        total += line_total
        total_cost += line_cost
    sale_return.total = money(total)
    sale_return.total_cost = money(total_cost)
    sale_return.profit_delta = money(total - total_cost)
    sale_return.save(update_fields=["total", "total_cost", "profit_delta", "updated_at"])
    all_returned = all(item.returnable_quantity == 0 for item in sale.items.all())
    sale.status = SaleStatus.RETURNED if all_returned else SaleStatus.PARTIALLY_RETURNED
    sale.version += 1
    sale.save(update_fields=["status", "version", "updated_at"])
    write_audit(
        user=user,
        action=AuditAction.SALE_RETURNED,
        entity_type="SaleReturn",
        entity_id=sale_return.id,
        new_data={"sale_id": sale.id, "total": str(sale_return.total)},
        reason=reason,
    )
    return sale_return


@transaction.atomic
def correct_sale(*, sale_id: int, items: list[dict], reason: str, expected_version: int, user=None) -> Sale:
    if not reason.strip():
        raise BusinessError("REASON_REQUIRED", "Укажите причину исправления.")
    sale = Sale.objects.select_for_update().prefetch_related("items").get(id=sale_id)
    if sale.version != expected_version:
        raise BusinessError("STALE_SALE", "Продажа была изменена другим пользователем.", {"current_version": sale.version})
    if sale.status != SaleStatus.COMPLETED:
        raise BusinessError("SALE_NOT_COMPLETED", "Исправлять можно только завершенную продажу без возвратов/отмены.")

    old_snapshot = _sale_snapshot(sale)
    existing = {item.id: item for item in sale.items.select_related("product")}
    total = Decimal("0")
    total_cost = Decimal("0")

    for payload in items:
        sale_item = existing.get(int(payload["sale_item_id"]))
        if sale_item is None:
            raise BusinessError("SALE_ITEM_NOT_FOUND", "Строка продажи не найдена.")
        new_qty = Decimal(str(payload["quantity"]))
        if new_qty <= 0:
            raise BusinessError("INVALID_QUANTITY", "Количество должно быть больше нуля.")
        product = Product.objects.select_for_update().get(id=sale_item.product_id)
        delta = new_qty - sale_item.quantity
        if delta > 0 and product.current_stock < delta:
            raise BusinessError("INSUFFICIENT_STOCK", "Недостаточно товара для увеличения продажи.")
        if delta > 0:
            apply_stock_movement(product=product, movement_type=InventoryMovementType.SALE, quantity=delta, user=user, reference_type="SaleCorrection", reference_id=sale.id, comment=reason)
        elif delta < 0:
            apply_stock_movement(product=product, movement_type=InventoryMovementType.SALE_RETURN, quantity=abs(delta), user=user, reference_type="SaleCorrection", reference_id=sale.id, comment=reason)
        calculated = _line_from_product(
            product,
            new_qty,
            Decimal(str(payload["unit_price"])) if payload.get("unit_price") is not None else sale_item.actual_unit_price,
            Decimal(str(payload["total_price"])) if payload.get("total_price") is not None else None,
        )
        sale_item.quantity = new_qty
        sale_item.actual_unit_price = calculated["actual_unit_price"]
        sale_item.line_total = calculated["line_total"]
        sale_item.line_cost = money(new_qty * sale_item.cost_price)
        sale_item.line_profit = money(sale_item.line_total - sale_item.line_cost)
        sale_item.save(update_fields=["quantity", "actual_unit_price", "line_total", "line_cost", "line_profit"])
        total += sale_item.line_total
        total_cost += sale_item.line_cost

    sale.subtotal = money(total)
    sale.total = money(total - sale.discount)
    sale.total_cost = money(total_cost)
    sale.profit = money(sale.total - sale.total_cost)
    sale.version += 1
    sale.save(update_fields=["subtotal", "total", "total_cost", "profit", "version", "updated_at"])
    write_audit(
        user=user,
        action=AuditAction.SALE_CORRECTED,
        entity_type="Sale",
        entity_id=sale.id,
        old_data=old_snapshot,
        new_data=_sale_snapshot(sale),
        reason=reason,
    )
    return sale


def _sale_snapshot(sale: Sale) -> dict:
    sale.refresh_from_db()
    return {
        "number": sale.number,
        "status": sale.status,
        "total": str(sale.total),
        "total_cost": str(sale.total_cost),
        "profit": str(sale.profit),
        "version": sale.version,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": str(item.quantity),
                "actual_unit_price": str(item.actual_unit_price),
                "line_total": str(item.line_total),
                "line_cost": str(item.line_cost),
                "line_profit": str(item.line_profit),
            }
            for item in sale.items.order_by("id")
        ],
    }
