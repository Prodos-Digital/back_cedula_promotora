from django.contrib import admin

from integration.admin_helpers import build_model_admin

from . import models as m

for _model in (m.EmpCliente, m.Emprestimo, m.EmprestimoParcela, m.Acordo, m.AcordoParcela):
    admin.site.register(_model, build_model_admin(_model))
