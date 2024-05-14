from django.contrib.auth import get_user_model
from rest_framework import serializers
from rolepermissions.roles import get_user_roles
from rolepermissions.checkers import has_permission

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    perms = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields= '__all__'
        read_only_field = ['is_active', 'created']

    def get_perms(self, obj):
        roles = get_user_roles(obj)
        permissions = {}
        for role in roles:
            permissions.update(role.available_permissions)
            for perm in role.available_permissions:
                permissions[perm] = has_permission(obj, perm)
        return permissions
