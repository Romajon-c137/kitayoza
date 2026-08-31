from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser", "groups", "permissions"]

    def get_permissions(self, obj):
        return sorted(obj.get_all_permissions())

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]
