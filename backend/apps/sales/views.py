from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response

from apps.sales.models import Sale
from apps.sales.serializers import (
    SaleCancelSerializer,
    SaleCorrectionSerializer,
    SaleCreateSerializer,
    SaleReturnCreateSerializer,
    SaleReturnSerializer,
    SaleSerializer,
)
from apps.sales.services import cancel_sale, complete_sale, correct_sale, create_sale_return


class SaleViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["status", "operator", "payment_method"]

    def get_queryset(self):
        return Sale.objects.select_related("operator", "customer").prefetch_related("items__product", "returns").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return SaleCreateSerializer
        return SaleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = complete_sale(
            payload=serializer.validated_data,
            user=request.user,
            idempotency_key=request.headers.get("Idempotency-Key"),
        )
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)
        return Response(SaleSerializer(result, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        serializer = SaleCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = cancel_sale(sale_id=pk, reason=serializer.validated_data["reason"], user=request.user)
        return Response(SaleSerializer(sale, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"])
    def returns(self, request, pk=None):
        serializer = SaleReturnCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale_return = create_sale_return(
            sale_id=pk,
            items=serializer.validated_data["items"],
            reason=serializer.validated_data["reason"],
            user=request.user,
        )
        return Response(SaleReturnSerializer(sale_return).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def correct(self, request, pk=None):
        serializer = SaleCorrectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = correct_sale(
            sale_id=pk,
            items=serializer.validated_data["items"],
            reason=serializer.validated_data["reason"],
            expected_version=serializer.validated_data["expected_version"],
            user=request.user,
        )
        return Response(SaleSerializer(sale, context=self.get_serializer_context()).data)
