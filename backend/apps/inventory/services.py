from decimal import Decimal

from django.db import transaction

from apps.audit.models import AuditAction
from apps.audit.services import write_audit
from apps.core.exceptions import BusinessError
from apps.products.models import Product
from apps.inventory.models import InventoryMovement, InventoryMovementType, StockAdjustment


POSITIVE_TYPES = {
    InventoryMovementType.INITIAL_BALANCE,
    InventoryMovementType.RECEIPT,
    InventoryMovementType.SALE_RETURN,
    InventoryMovementType.ADJUSTMENT_IN,
    InventoryMovementType.SALE_CANCEL,
}


def apply_stock_movement(
    *,
    product: Product,
    movement_type: str,
    quantity: Decimal,
    user=None,
    reference_type: str = "",
    reference_id: str | int = "",
    comment: str = "",
) -> InventoryMovement:
    if quantity <= 0:
        raise BusinessError("INVALID_QUANTITY", "Количество должно быть больше нуля.", {"quantity": str(quantity)})

    signed_quantity = quantity if movement_type in POSITIVE_TYPES else -quantity
    stock_before = product.current_stock
    stock_after = stock_before + signed_quantity
    if stock_after < 0:
        raise BusinessError(
            "INSUFFICIENT_STOCK",
            "Недостаточно товара на складе.",
            {"product_id": product.id, "available": str(stock_before), "requested": str(quantity)},
        )

    product.current_stock = stock_after
    product.save(update_fields=["current_stock", "updated_at"])
    return InventoryMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=signed_quantity,
        stock_before=stock_before,
        stock_after=stock_after,
        reference_type=reference_type,
        reference_id=str(reference_id) if reference_id else "",
        user=user if getattr(user, "is_authenticated", False) else None,
        comment=comment,
    )


@transaction.atomic
def adjust_stock(*, product_id: int, quantity_delta: Decimal, reason: str, user=None) -> StockAdjustment:
    if not reason.strip():
        raise BusinessError("REASON_REQUIRED", "Укажите причину корректировки.")
    product = Product.objects.select_for_update().get(id=product_id)
    movement_type = InventoryMovementType.ADJUSTMENT_IN if quantity_delta > 0 else InventoryMovementType.ADJUSTMENT_OUT
    movement = apply_stock_movement(
        product=product,
        movement_type=movement_type,
        quantity=abs(quantity_delta),
        user=user,
        reference_type="StockAdjustment",
        comment=reason,
    )
    adjustment = StockAdjustment.objects.create(
        product=product,
        quantity_delta=quantity_delta,
        reason=reason,
        created_by=user if getattr(user, "is_authenticated", False) else None,
        movement=movement,
    )
    movement.reference_id = adjustment.id
    movement.save(update_fields=["reference_id"])
    write_audit(
        user=user,
        action=AuditAction.STOCK_ADJUSTED,
        entity_type="StockAdjustment",
        entity_id=adjustment.id,
        new_data={"product_id": product.id, "quantity_delta": str(quantity_delta)},
        reason=reason,
    )
    return adjustment
