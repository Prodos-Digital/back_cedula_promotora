"""
Helpers partilhados pelos ModelAdmin gerados (core, empréstimos).
Evita 500 no admin por list_display com FK ou search em UUID.
"""
from django.contrib import admin
from django.db import connection
from django.db import models as dj_models


def _skip_list_field(f) -> bool:
    if f.name == "password":
        return True
    return isinstance(
        f,
        (
            dj_models.ForeignKey,
            dj_models.OneToOneField,
            dj_models.ManyToManyField,
        ),
    )


def list_display_for_model(model, max_fields: int = 8):
    names = [f.name for f in model._meta.concrete_fields if not _skip_list_field(f)]
    if "id" in names:
        names.remove("id")
        ordered = ["id"] + names
    else:
        ordered = names
    out = tuple(ordered[:max_fields])
    return out if out else ("id",)


def search_fields_for_model(model, max_fields: int = 5):
    """Só texto: nunca UUID (Postgres não suporta ILIKE em uuid)."""
    out = []
    for f in model._meta.fields:
        if isinstance(
            f,
            (
                dj_models.CharField,
                dj_models.TextField,
                dj_models.EmailField,
            ),
        ):
            if f.name not in ("password", "senha"):
                out.append(f.name)
        if len(out) >= max_fields:
            break
    return tuple(out)


class UnmanagedMissingTableGuardMixin:
    """
    Modelos unmanaged com tabela ainda inexistente na BD (ex.: dump não importado).
    Sem isto, o changelist faz COUNT e devolve 500 (ProgrammingError).
    """

    def _integration_table_exists(self, request):
        meta = self.model._meta
        if meta.managed or not meta.db_table:
            return True
        cache = getattr(request, "_integration_admin_table_exists", None)
        if cache is None:
            cache = {}
            request._integration_admin_table_exists = cache
        t = meta.db_table
        if t not in cache:
            cache[t] = t in connection.introspection.table_names()
        return cache[t]

    def _integration_table_missing(self, request):
        meta = self.model._meta
        if meta.managed or not meta.db_table:
            return False
        return not self._integration_table_exists(request)

    def get_queryset(self, request):
        if self._integration_table_missing(request):
            return self.model.objects.none()
        return super().get_queryset(request)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if self._integration_table_missing(request):
            extra_context["integration_missing_db_table"] = self.model._meta.db_table
        return super().changelist_view(request, extra_context)


class UnmanagedNoAddDeleteMixin:
    """managed=False: não criar nem apagar linhas pelo admin."""

    def has_add_permission(self, request):
        if self.model._meta.managed is False:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if self.model._meta.managed is False:
            return False
        return super().has_delete_permission(request, obj)


def build_model_admin(model):
    name = f"{model.__name__}Admin"
    attrs = {
        "list_display": list_display_for_model(model),
        "search_fields": search_fields_for_model(model),
        "list_per_page": 50,
        "show_full_result_count": False,
        "change_list_template": "admin/integration_unmanaged_changelist.html",
    }
    bases = (
        UnmanagedMissingTableGuardMixin,
        UnmanagedNoAddDeleteMixin,
        admin.ModelAdmin,
    )
    return type(name, bases, attrs)
