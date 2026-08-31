from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ["created_at", "action", "entity_type", "entity_id", "user", "reason"]
    list_filter = ["action", "entity_type", "created_at", "user"]
    search_fields = ["entity_id", "reason", "old_data", "new_data"]
    readonly_fields = [field.name for field in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
