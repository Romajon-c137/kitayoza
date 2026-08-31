from datetime import datetime

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reports.services import dashboard_summary, operator_report, product_report, product_report_csv


def _date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


class DashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(dashboard_summary(_date(request.query_params.get("date_from")), _date(request.query_params.get("date_to"))))


class ProductReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = product_report(
            date_from=_date(request.query_params.get("date_from")),
            date_to=_date(request.query_params.get("date_to")),
            product_id=request.query_params.get("product"),
            category_id=request.query_params.get("category"),
            sku=request.query_params.get("sku"),
            operator_id=request.query_params.get("operator"),
            ordering=request.query_params.get("ordering", "highest_revenue"),
        )
        if request.query_params.get("format") == "csv":
            response = HttpResponse(product_report_csv(rows), content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="product-report.csv"'
            return response
        return Response(rows)


class OperatorReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(operator_report(_date(request.query_params.get("date_from")), _date(request.query_params.get("date_to"))))
