from rest_framework import serializers

from apps.inventory.models import InventoryMovement, StockAdjustment


class InventoryMovementSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = InventoryMovement
        fields = "__all__"


class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustment
        fields = ["id", "product", "quantity_delta", "reason", "created_by", "movement", "created_at", "updated_at"]
        read_only_fields = ["created_by", "movement", "created_at", "updated_at"]
