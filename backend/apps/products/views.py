from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from apps.products.models import Category, Product
from apps.products.serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("parent").order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["is_active", "parent"]
    search_fields = ["name", "slug"]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ["is_active", "category", "unit"]
    search_fields = ["name", "sku", "model", "brand"]

    def get_queryset(self):
        queryset = Product.objects.select_related("category").order_by("name")
        query = self.request.query_params.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(sku__icontains=query)
                | Q(model__icontains=query)
                | Q(brand__icontains=query)
            )
        return queryset
