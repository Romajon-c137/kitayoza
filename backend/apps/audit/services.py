from django.contrib.auth import get_user_model

from apps.audit.models import AuditLog

User = get_user_model()


def write_audit(
    *,
    user: User | None,
    action: str,
    entity_type: str,
    entity_id: str | int,
    old_data: dict | None = None,
    new_data: dict | None = None,
    reason: str = "",
    ip_address: str | None = None,
) -> AuditLog:
    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        old_data=old_data or {},
        new_data=new_data or {},
        reason=reason,
        ip_address=ip_address,
    )
