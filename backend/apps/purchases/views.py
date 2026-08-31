from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response

from apps.purchases.models import StockReceipt
from apps.purchases.serializers import StockReceiptSerializer
from apps.purchases.services import cancel_receipt, post_receipt


class StockReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = StockReceiptSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["status", "supplier", "date"]

    def get_queryset(self):
        return StockReceipt.objects.select_related("supplier", "created_by").prefetch_related("items__product").order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def post(self, request, pk=None):
        receipt = post_receipt(receipt_id=pk, user=request.user)
        return Response(self.get_serializer(receipt).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        receipt = cancel_receipt(receipt_id=pk, reason=request.data.get("reason", ""), user=request.user)
        return Response(self.get_serializer(receipt).data, status=status.HTTP_200_OK)
