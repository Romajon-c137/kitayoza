from rest_framework import serializers

from apps.purchases.models import StockReceipt, StockReceiptItem


class StockReceiptItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = StockReceiptItem
        fields = ["id", "product", "product_sku", "product_name", "quantity", "cost_price", "line_total"]
        read_only_fields = ["line_total"]


class StockReceiptSerializer(serializers.ModelSerializer):
    items = StockReceiptItemSerializer(many=True)

    class Meta:
        model = StockReceipt
        fields = [
            "id",
            "number",
            "supplier",
            "status",
            "date",
            "comment",
            "total",
            "created_by",
            "posted_at",
            "cancelled_at",
            "cancel_reason",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["number", "status", "total", "created_by", "posted_at", "cancelled_at", "cancel_reason", "created_at", "updated_at"]

    def create(self, validated_data):
        items = validated_data.pop("items")
        receipt = StockReceipt.objects.create(**validated_data)
        for item in items:
            StockReceiptItem.objects.create(receipt=receipt, **item)
        return receipt

    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items is not None:
            instance.items.all().delete()
            for item in items:
                StockReceiptItem.objects.create(receipt=instance, **item)
        return instance
