from django.contrib import admin

from integration.admin_helpers import build_model_admin

from . import models as m

_ORDERED = (
    m.Cliente,
    m.Contrato,
    m.PreContrato,
    m.FuturoContrato,
    m.Despesa,
    m.Emprestimo,
    m.EmprestimoItem,
    m.Lojas,
    m.Promotora,
    m.Convenio,
    m.Operacao,
    m.Banco,
    m.Corretor,
    m.NaturezaDespesa,
    m.CanalAquisicaoCliente,
)

for _model in _ORDERED:
    admin.site.register(_model, build_model_admin(_model))
