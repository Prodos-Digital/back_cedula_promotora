from rolepermissions.roles import AbstractUserRole
# https://django-role-permissions.readthedocs.io/en/stable/utils.html

class MenuPermissions(AbstractUserRole):
    available_permissions = {
        'menu_acessos': False,
        'menu_cadastros': False,
        'menu_configuracoes': False,
        'menu_dashboards': False,
        'menu_relatorios': False,
    }

class AppPermissions(AbstractUserRole):
    available_permissions = {
        'app_usuarios': False,
        'app_cadastro_cliente': False,
        'app_cadastro_contrato': False,
        'app_cadastro_despesa': False,
        'app_cadastro_pre_contrato': False,
        'app_cadastro_futuro_contrato': False,
        'app_config_bancos': False,
        'app_config_convenios': False,
        'app_config_corretores': False,
        'app_config_lojas': False,
        'app_config_operacoes': False,
        'app_config_promotoras': False,
        'app_config_aquisicao_clientes': False,
        'app_config_natureza_despesas': False,
        'app_dash_clientes': False,
        'app_dash_contratos': False,
        'app_dash_despesas': False,
        'app_relatorio_clientes': False,
        'app_relatorio_clientes_dos_operadores': False,
        'app_relatorio_contratos': False,
        'app_relatorio_despesas': False,
        'app_relatorio_pre_contratos': False,
        'app_relatorio_futuro_contrato': False,
    }

