"""Filtros para agrupar apps no índice do Django Admin (Cédula vs empréstimos)."""
from django import template

register = template.Library()

_CEDULA = frozenset({"core"})
_EMPRESTIMOS = frozenset({"emprestimos"})
_CONTAS = frozenset({"users_module", "auth"})


@register.filter
def apps_for_section(app_list, section: str):
    """
    section: 'cedula' | 'emprestimos' | 'contas' | 'outros'
    app_list: lista de dicts do AdminSite (name, app_label, app_url, models).
    """
    if not app_list:
        return []
    key = (section or "").strip().lower()
    if key == "cedula":
        return [a for a in app_list if a.get("app_label") in _CEDULA]
    if key == "emprestimos":
        return [a for a in app_list if a.get("app_label") in _EMPRESTIMOS]
    if key == "contas":
        return [a for a in app_list if a.get("app_label") in _CONTAS]
    if key == "outros":
        skip = _CEDULA | _EMPRESTIMOS | _CONTAS
        return [a for a in app_list if a.get("app_label") not in skip]
    return []
