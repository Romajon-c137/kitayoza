from rest_framework import serializers

from apps.products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "category",
            "brand",
            "model",
            "size",
            "color",
            "unit",
            "unit_display",
            "description",
            "image",
            "image_url",
            "cost_price",
            "sale_price",
            "current_stock",
            "minimum_stock",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["current_stock", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if not obj.image:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url
