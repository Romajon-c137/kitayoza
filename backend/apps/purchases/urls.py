from rest_framework.routers import DefaultRouter

from apps.purchases.views import StockReceiptViewSet

router = DefaultRouter()
router.register("receipts", StockReceiptViewSet, basename="stock-receipt")

urlpatterns = router.urls
