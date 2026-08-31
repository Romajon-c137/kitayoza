from decimal import Decimal

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.audit.models import AuditAction
from apps.audit.services import write_audit
from apps.core.decimal import money
from apps.core.exceptions import BusinessError
from apps.inventory.models import InventoryMovementType
from apps.inventory.services import apply_stock_movement
from apps.products.models import Product
from apps.purchases.models import ReceiptStatus, StockReceipt


def next_receipt_number() -> str:
    year = timezone.localdate().year
    max_id = (StockReceipt.objects.aggregate(value=Max("id"))["value"] or 0) + 1
    return f"REC-{year}-{max_id:06d}"


@transaction.atomic
def post_receipt(*, receipt_id: int, user=None) -> StockReceipt:
    receipt = StockReceipt.objects.select_for_update().prefetch_related("items").get(id=receipt_id)
    if receipt.status != ReceiptStatus.DRAFT:
        raise BusinessError("RECEIPT_NOT_DRAFT", "Можно провести только черновик прихода.")
    if not receipt.items.exists():
        raise BusinessError("EMPTY_RECEIPT", "В приходе нет товаров.")

    total = Decimal("0")
    for item in receipt.items.select_related("product"):
        if not item.product.is_active:
            raise BusinessError("INACTIVE_PRODUCT", "Нельзя принять неактивный товар.", {"product_id": item.product_id})
        product = Product.objects.select_for_update().get(id=item.product_id)
        item.line_total = money(item.quantity * item.cost_price)
        item.save(update_fields=["line_total"])
        total += item.line_total
        apply_stock_movement(
            product=product,
            movement_type=InventoryMovementType.RECEIPT,
            quantity=item.quantity,
            user=user,
            reference_type="StockReceipt",
            reference_id=receipt.id,
            comment=receipt.comment,
        )
        old_cost = product.cost_price
        product.cost_price = item.cost_price
        product.save(update_fields=["cost_price", "updated_at"])
        if old_cost != product.cost_price:
            write_audit(
                user=user,
                action=AuditAction.COST_PRICE_CHANGED,
                entity_type="Product",
                entity_id=product.id,
                old_data={"cost_price": str(old_cost)},
                new_data={"cost_price": str(product.cost_price)},
                reason=f"Приход {receipt.number or receipt.id}",
            )

    receipt.total = money(total)
    receipt.status = ReceiptStatus.POSTED
    receipt.posted_at = timezone.now()
    if not receipt.number:
        receipt.number = next_receipt_number()
    receipt.save(update_fields=["total", "status", "posted_at", "number", "updated_at"])
    write_audit(
        user=user,
        action=AuditAction.RECEIPT_POSTED,
        entity_type="StockReceipt",
        entity_id=receipt.id,
        new_data={"number": receipt.number, "total": str(receipt.total)},
    )
    return receipt


@transaction.atomic
def cancel_receipt(*, receipt_id: int, reason: str, user=None) -> StockReceipt:
    if not reason.strip():
        raise BusinessError("REASON_REQUIRED", "Укажите причину отмены прихода.")
    receipt = StockReceipt.objects.select_for_update().prefetch_related("items").get(id=receipt_id)
    if receipt.status != ReceiptStatus.POSTED:
        raise BusinessError("RECEIPT_NOT_POSTED", "Можно отменить только проведенный приход.")
    for item in receipt.items.select_related("product"):
        product = Product.objects.select_for_update().get(id=item.product_id)
        apply_stock_movement(
            product=product,
            movement_type=InventoryMovementType.RECEIPT_CANCEL,
            quantity=item.quantity,
            user=user,
            reference_type="StockReceipt",
            reference_id=receipt.id,
            comment=reason,
        )
    receipt.status = ReceiptStatus.CANCELLED
    receipt.cancelled_at = timezone.now()
    receipt.cancel_reason = reason
    receipt.save(update_fields=["status", "cancelled_at", "cancel_reason", "updated_at"])
    write_audit(
        user=user,
        action=AuditAction.RECEIPT_CANCELLED,
        entity_type="StockReceipt",
        entity_id=receipt.id,
        reason=reason,
    )
    return receipt
