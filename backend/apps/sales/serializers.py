from rest_framework import serializers

from apps.sales.models import Sale, SaleItem, SaleReturn


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_size",
            "product_unit",
            "quantity",
            "returned_quantity",
            "cost_price",
            "regular_sale_price",
            "actual_unit_price",
            "line_total",
            "line_cost",
            "line_profit",
        ]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    operator_name = serializers.CharField(source="operator.username", read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "number",
            "status",
            "operator",
            "operator_name",
            "customer",
            "subtotal",
            "discount",
            "total",
            "total_cost",
            "profit",
            "payment_method",
            "comment",
            "completed_at",
            "cancelled_by",
            "cancelled_at",
            "cancel_reason",
            "version",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SaleCreateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3)
    unit_price = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    total_price = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)

    def validate(self, attrs):
        if attrs.get("unit_price") is not None and attrs.get("total_price") is not None:
            raise serializers.ValidationError("Укажите либо цену за единицу, либо сумму строки.")
        return attrs


class SaleCreateSerializer(serializers.Serializer):
    items = SaleCreateItemSerializer(many=True)
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    payment_method = serializers.ChoiceField(choices=["cash", "card", "transfer", "other"], default="cash")
    comment = serializers.CharField(required=False, allow_blank=True)


class SaleCancelSerializer(serializers.Serializer):
    reason = serializers.CharField()


class SaleReturnItemInputSerializer(serializers.Serializer):
    sale_item_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3)


class SaleReturnCreateSerializer(serializers.Serializer):
    reason = serializers.CharField()
    items = SaleReturnItemInputSerializer(many=True)


class SaleCorrectionSerializer(serializers.Serializer):
    reason = serializers.CharField()
    expected_version = serializers.IntegerField()
    items = serializers.ListField(child=serializers.DictField())


class SaleReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReturn
        fields = "__all__"
