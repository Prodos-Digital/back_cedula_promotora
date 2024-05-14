from rolepermissions.roles import AbstractUserRole

class MenuPermissions(AbstractUserRole):
    available_permissions = {
        'menu_acessos': True,
    }

class AppPermissions(AbstractUserRole):
    available_permissions = {
        'app_usuarios': True,
    }