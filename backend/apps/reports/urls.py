from django.urls import path

from apps.reports.views import DashboardReportView, OperatorReportView, ProductReportView

urlpatterns = [
    path("dashboard/", DashboardReportView.as_view(), name="dashboard-report"),
    path("products/", ProductReportView.as_view(), name="product-report"),
    path("operators/", OperatorReportView.as_view(), name="operator-report"),
    path("sales/", DashboardReportView.as_view(), name="sales-report"),
]
