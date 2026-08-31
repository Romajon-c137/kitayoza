from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ["name", "contact_person", "phone", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "contact_person", "phone"]
