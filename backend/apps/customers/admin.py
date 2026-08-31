from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.customers.models import Customer


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ["name", "company_name", "phone", "created_at"]
    search_fields = ["name", "company_name", "phone"]
