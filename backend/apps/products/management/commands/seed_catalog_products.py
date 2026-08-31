from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.inventory.services import adjust_stock
from apps.products.models import Category, Product, ProductUnit

User = get_user_model()


PRODUCTS = [
    {
        "sku": "WC-AURA-WHITE",
        "name": "无边坐便器 Aura 白色",
        "category": "马桶 / Унитазы",
        "brand": "Aura",
        "model": "Rimless",
        "size": "标准",
        "unit": ProductUnit.PCS,
        "cost_price": Decimal("2800"),
        "sale_price": Decimal("4200"),
        "minimum_stock": Decimal("5"),
        "initial_stock": Decimal("30"),
        "image": "products/toilet-modern-rimless.png",
    },
    {
        "sku": "WC-MONACO-BASIC",
        "name": "连体坐便器 Monaco 带盖板 白色",
        "category": "马桶 / Унитазы",
        "brand": "Monaco",
        "model": "Basic",
        "size": "标准",
        "unit": ProductUnit.PCS,
        "cost_price": Decimal("2500"),
        "sale_price": Decimal("3900"),
        "minimum_stock": Decimal("5"),
        "initial_stock": Decimal("24"),
        "image": "products/toilet-modern-rimless.png",
    },
    {
        "sku": "SHOWER-BLACK-RAIN",
        "name": "黑色淋浴花洒套装 300毫米顶喷",
        "category": "淋浴系统 / Душевые системы",
        "brand": "Rain",
        "model": "Black",
        "size": "300毫米顶喷",
        "color": "黑色",
        "unit": ProductUnit.SET,
        "cost_price": Decimal("3200"),
        "sale_price": Decimal("5200"),
        "minimum_stock": Decimal("4"),
        "initial_stock": Decimal("18"),
        "image": "products/shower-system-rain-black.png",
    },
    {
        "sku": "SHOWER-WHITE-RAIN",
        "name": "白色淋浴花洒套装 300毫米顶喷",
        "category": "淋浴系统 / Душевые системы",
        "brand": "Rain",
        "model": "White",
        "size": "300毫米顶喷",
        "color": "白色",
        "unit": ProductUnit.SET,
        "cost_price": Decimal("3300"),
        "sale_price": Decimal("5400"),
        "minimum_stock": Decimal("4"),
        "initial_stock": Decimal("16"),
        "image": "products/shower-system-rain-white.png",
    },
    {
        "sku": "FAUCET-KITCHEN-BLACK",
        "name": "黑色抽拉式厨房水龙头",
        "category": "水龙头 / Смесители",
        "brand": "KTJO",
        "model": "Flexible",
        "color": "黑色",
        "unit": ProductUnit.PCS,
        "cost_price": Decimal("950"),
        "sale_price": Decimal("1550"),
        "minimum_stock": Decimal("10"),
        "initial_stock": Decimal("45"),
        "image": "products/kitchen-faucet-flex-black.png",
    },
    {
        "sku": "FAUCET-KITCHEN-WHITE",
        "name": "白色抽拉式厨房水龙头",
        "category": "水龙头 / Смесители",
        "brand": "KTJO",
        "model": "Flexible",
        "color": "白色",
        "unit": ProductUnit.PCS,
        "cost_price": Decimal("980"),
        "sale_price": Decimal("1600"),
        "minimum_stock": Decimal("10"),
        "initial_stock": Decimal("40"),
        "image": "products/kitchen-faucet-flex-white.png",
    },
    {
        "sku": "TILE-CALACATTA-60120-GOLD",
        "name": "卡拉卡塔金瓷砖 60x120厘米",
        "category": "瓷砖 / Керамогранит",
        "brand": "Calacatta",
        "model": "Gold",
        "size": "60x120",
        "color": "白色 / 金色",
        "unit": ProductUnit.M2,
        "cost_price": Decimal("900"),
        "sale_price": Decimal("1350"),
        "minimum_stock": Decimal("25"),
        "initial_stock": Decimal("180"),
        "image": "products/tile-calacatta.png",
    },
    {
        "sku": "TILE-CALACATTA-6060-GOLD",
        "name": "卡拉卡塔金墙砖 60x60厘米",
        "category": "墙砖 / Кафель",
        "brand": "Calacatta",
        "model": "Gold",
        "size": "60x60",
        "color": "白色 / 金色",
        "unit": ProductUnit.M2,
        "cost_price": Decimal("780"),
        "sale_price": Decimal("1180"),
        "minimum_stock": Decimal("25"),
        "initial_stock": Decimal("220"),
        "image": "products/tile-calacatta.png",
    },
    {
        "sku": "SOLAR-BULB-KIT-4",
        "name": "太阳能LED灯套装 4灯",
        "category": "太阳能灯 / Лампочки на солнечной панели",
        "brand": "Solar",
        "model": "Kit 4",
        "size": "4灯",
        "unit": ProductUnit.SET,
        "cost_price": Decimal("650"),
        "sale_price": Decimal("1100"),
        "minimum_stock": Decimal("10"),
        "initial_stock": Decimal("60"),
        "image": "products/solar-bulb-kit.png",
    },
    {
        "sku": "SOLAR-BULB-KIT-6",
        "name": "太阳能LED灯套装 6灯",
        "category": "太阳能灯 / Лампочки на солнечной панели",
        "brand": "Solar",
        "model": "Kit 6",
        "size": "6灯",
        "unit": ProductUnit.SET,
        "cost_price": Decimal("850"),
        "sale_price": Decimal("1450"),
        "minimum_stock": Decimal("10"),
        "initial_stock": Decimal("50"),
        "image": "products/solar-bulb-kit.png",
    },
]


class Command(BaseCommand):
    help = "Create catalog demo products with images and initial stock."

    def handle(self, *args, **options):
        admin = User.objects.filter(is_superuser=True).order_by("id").first()
        roots = {
            "卫浴 / Сантехника": Category.objects.update_or_create(slug="santehnika", defaults={"name": "卫浴 / Сантехника"})[0],
            "瓷砖 / Плитка": Category.objects.update_or_create(slug="plitka", defaults={"name": "瓷砖 / Плитка"})[0],
            "电器 / Электрика": Category.objects.update_or_create(slug="elektrika", defaults={"name": "电器 / Электрика"})[0],
        }
        category_parents = {
            "马桶 / Унитазы": roots["卫浴 / Сантехника"],
            "淋浴系统 / Душевые системы": roots["卫浴 / Сантехника"],
            "水龙头 / Смесители": roots["卫浴 / Сантехника"],
            "墙砖 / Кафель": roots["瓷砖 / Плитка"],
            "瓷砖 / Керамогранит": roots["瓷砖 / Плитка"],
            "太阳能灯 / Лампочки на солнечной панели": roots["电器 / Электрика"],
        }
        categories = {}
        slugs = {
            "马桶 / Унитазы": "unitazy",
            "淋浴系统 / Душевые системы": "dushevye-sistemy",
            "水龙头 / Смесители": "smesiteli",
            "墙砖 / Кафель": "kafel",
            "瓷砖 / Керамогранит": "keramogranit",
            "太阳能灯 / Лампочки на солнечной панели": "solnechnye-lampy",
        }
        for name, parent in category_parents.items():
            categories[name] = Category.objects.update_or_create(
                slug=slugs[name],
                defaults={"name": name, "parent": parent, "is_active": True},
            )[0]
        Category.objects.update_or_create(
            slug="dushevye-trapy",
            defaults={"name": "地漏 / Душевые трапы", "parent": roots["卫浴 / Сантехника"], "is_active": True},
        )

        created_count = 0
        updated_count = 0
        for item in PRODUCTS:
            data = item.copy()
            initial_stock = data.pop("initial_stock")
            category_name = data.pop("category")
            product, created = Product.objects.update_or_create(
                sku=data["sku"],
                defaults={**data, "category": categories[category_name], "is_active": True},
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
            if product.current_stock == 0 and initial_stock > 0:
                adjust_stock(
                    product_id=product.id,
                    quantity_delta=initial_stock,
                    reason="Начальный остаток для демонстрационного каталога",
                    user=admin,
                )

        archived = Product.objects.filter(image="").update(is_active=False)
        archived_categories = Category.objects.filter(
            slug__in=["душевые-системы", "керамогранит", "лампочки-на-солнечной-панели"]
        ).update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"Catalog products ready. Created: {created_count}, updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Products without images archived: {archived}"))
        self.stdout.write(self.style.WARNING(f"Unused duplicate categories archived: {archived_categories}"))
