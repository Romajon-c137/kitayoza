from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.inventory.services import adjust_stock
from apps.products.models import Category, Product, ProductUnit

User = get_user_model()


class Command(BaseCommand):
    help = "Create development users, groups, categories and products."

    def handle(self, *args, **options):
        operator_group, _ = Group.objects.get_or_create(name="OPERATOR")
        admin_group, _ = Group.objects.get_or_create(name="ADMIN")

        operator_permissions = Permission.objects.filter(
            content_type__app_label__in=["products", "sales"],
            codename__in=["view_product", "add_sale", "view_sale"],
        )
        operator_group.permissions.set(operator_permissions)

        admin_group.permissions.set(Permission.objects.exclude(content_type__app_label="admin"))

        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True})
        admin.set_password("admin12345")
        admin.save()

        operator, _ = User.objects.get_or_create(username="operator", defaults={"email": "operator@example.com"})
        operator.set_password("operator12345")
        operator.groups.add(operator_group)
        operator.save()

        plumbing, _ = Category.objects.get_or_create(name="Сантехника", defaults={"slug": "santehnika"})
        tiles, _ = Category.objects.get_or_create(name="Плитка", defaults={"slug": "plitka"})
        categories = [
            ("Унитазы", "unitazy", plumbing),
            ("Смесители", "smesiteli", plumbing),
            ("Душевые трапы", "dushevye-trapy", plumbing),
            ("Кафель", "kafel", tiles),
        ]
        for name, slug, parent in categories:
            Category.objects.get_or_create(name=name, defaults={"slug": slug, "parent": parent})

        products = [
            {"sku": "WC-MONACO", "name": "Унитаз Monaco Rimless", "category": Category.objects.get(slug="unitazy"), "unit": ProductUnit.PCS, "cost_price": Decimal("800"), "sale_price": Decimal("1200"), "minimum_stock": Decimal("5")},
            {"sku": "DRAIN-CHROME-600", "name": "Душевой трап Chrome 600", "category": Category.objects.get(slug="dushevye-trapy"), "unit": ProductUnit.PCS, "cost_price": Decimal("350"), "sale_price": Decimal("550"), "minimum_stock": Decimal("10")},
            {"sku": "TILE-CALACATTA-60120", "name": "Керамогранит Calacatta Gold 60x120", "category": Category.objects.get(slug="kafel"), "unit": ProductUnit.M2, "cost_price": Decimal("900"), "sale_price": Decimal("1350"), "minimum_stock": Decimal("20")},
        ]
        for data in products:
            product, created = Product.objects.get_or_create(sku=data["sku"], defaults=data)
            if created:
                adjust_stock(product_id=product.id, quantity_delta=Decimal("100"), reason="Начальный dev остаток", user=admin)

        self.stdout.write(self.style.SUCCESS("Seed data created. admin/admin12345, operator/operator12345"))
