import csv
from decimal import Decimal
from io import StringIO

from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.sales.models import Sale, SaleItem, SaleStatus


def _period_bounds(date_from=None, date_to=None):
    tz = timezone.get_current_timezone()
    if date_from is None:
        date_from = timezone.localdate()
    if date_to is None:
        date_to = date_from
    start = timezone.make_aware(timezone.datetime.combine(date_from, timezone.datetime.min.time()), tz)
    end = timezone.make_aware(timezone.datetime.combine(date_to, timezone.datetime.max.time()), tz)
    return start, end


def sales_queryset(date_from=None, date_to=None):
    start, end = _period_bounds(date_from, date_to)
    return Sale.objects.filter(completed_at__gte=start, completed_at__lte=end).exclude(status=SaleStatus.CANCELLED)


def dashboard_summary(date_from=None, date_to=None):
    qs = sales_queryset(date_from, date_to)
    data = qs.aggregate(
        revenue=Coalesce(Sum("total"), Decimal("0")),
        cost=Coalesce(Sum("total_cost"), Decimal("0")),
        profit=Coalesce(Sum("profit"), Decimal("0")),
        sales_count=Count("id"),
    )
    data["average_check"] = data["revenue"] / data["sales_count"] if data["sales_count"] else Decimal("0")
    return data


def product_report(date_from=None, date_to=None, product_id=None, category_id=None, sku=None, operator_id=None, ordering="-revenue"):
    sale_ids = sales_queryset(date_from, date_to).values("id")
    qs = SaleItem.objects.filter(sale_id__in=sale_ids).select_related("product", "sale")
    if product_id:
        qs = qs.filter(product_id=product_id)
    if category_id:
        qs = qs.filter(product__category_id=category_id)
    if sku:
        qs = qs.filter(product_sku__icontains=sku)
    if operator_id:
        qs = qs.filter(sale__operator_id=operator_id)
    rows = qs.values("product_id", "product_sku", "product_name", "product_size", "product_unit").annotate(
        quantity=Coalesce(Sum("quantity"), Decimal("0")),
        revenue=Coalesce(Sum("line_total"), Decimal("0")),
        cost=Coalesce(Sum("line_cost"), Decimal("0")),
        profit=Coalesce(Sum("line_profit"), Decimal("0")),
    )
    allowed = {
        "highest_revenue": "-revenue",
        "highest_profit": "-profit",
        "highest_quantity": "-quantity",
        "lowest_margin": "profit",
        "highest_margin": "-profit",
    }
    rows = rows.order_by(allowed.get(ordering, "-revenue"))
    result = []
    for row in rows:
        quantity = row["quantity"] or Decimal("0")
        revenue = row["revenue"] or Decimal("0")
        profit = row["profit"] or Decimal("0")
        row["average_sale_price"] = revenue / quantity if quantity else Decimal("0")
        row["margin"] = (profit / revenue * Decimal("100")) if revenue else Decimal("0")
        result.append(row)
    return result


def operator_report(date_from=None, date_to=None):
    qs = sales_queryset(date_from, date_to)
    rows = qs.values("operator_id", "operator__username").annotate(
        sales_count=Count("id"),
        revenue=Coalesce(Sum("total"), Decimal("0")),
        cost=Coalesce(Sum("total_cost"), Decimal("0")),
        profit=Coalesce(Sum("profit"), Decimal("0")),
        items_quantity=Coalesce(Sum("items__quantity"), Decimal("0")),
    ).order_by("-revenue")
    for row in rows:
        row["average_check"] = row["revenue"] / row["sales_count"] if row["sales_count"] else Decimal("0")
    return list(rows)


def product_report_csv(rows):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["SKU", "Товар", "Размер", "Ед.", "Количество", "Средняя цена", "Выручка", "Себестоимость", "Валовая прибыль", "Маржа"])
    for row in rows:
        writer.writerow([
            row["product_sku"],
            row["product_name"],
            row["product_size"],
            row["product_unit"],
            row["quantity"],
            row["average_sale_price"],
            row["revenue"],
            row["cost"],
            row["profit"],
            row["margin"],
        ])
    return output.getvalue()
