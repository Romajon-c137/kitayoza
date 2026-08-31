from rest_framework.routers import DefaultRouter

from apps.inventory.views import InventoryMovementViewSet, StockAdjustmentViewSet

router = DefaultRouter()
router.register("movements", InventoryMovementViewSet, basename="inventory-movement")
router.register("adjustments", StockAdjustmentViewSet, basename="stock-adjustment")

urlpatterns = router.urls
