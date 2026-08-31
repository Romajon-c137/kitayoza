from decimal import Decimal

from rest_framework import mixins, viewsets
from rest_framework.permissions import DjangoModelPermissions

from apps.inventory.models import InventoryMovement, StockAdjustment
from apps.inventory.serializers import InventoryMovementSerializer, StockAdjustmentSerializer
from apps.inventory.services import adjust_stock


class InventoryMovementViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = InventoryMovementSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["product", "movement_type", "reference_type", "reference_id"]

    def get_queryset(self):
        return InventoryMovement.objects.select_related("product", "user").order_by("-created_at")


class StockAdjustmentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = StockAdjustmentSerializer
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        return StockAdjustment.objects.select_related("product", "created_by", "movement").order_by("-created_at")

    def perform_create(self, serializer):
        adjustment = adjust_stock(
            product_id=serializer.validated_data["product"].id,
            quantity_delta=Decimal(serializer.validated_data["quantity_delta"]),
            reason=serializer.validated_data["reason"],
            user=self.request.user,
        )
        serializer.instance = adjustment
