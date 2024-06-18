import uuid
from django.db import models

class EmpCliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    nome = models.CharField(max_length=200, null=True, blank=True)
    dt_nascimento = models.DateField(null=True, blank=True)    
    telefone = models.CharField(max_length=20, null=True, blank=True)
    cep = models.CharField(max_length=8, null=True, blank=True)
    logradouro = models.CharField(max_length=120, null=True, blank=True)
    complemento = models.CharField(max_length=120, null=True, blank=True)
    bairro = models.CharField(max_length=60, null=True, blank=True)
    cidade = models.CharField(max_length=60, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'emp_clientes'

class Emprestimo(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    nome = models.CharField(max_length=200, null=True, blank=True)
    vl_emprestimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    # vl_tt_emprestimo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) Verificar necessidade desse campo
    vl_capital_giro = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    perc_juros = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    qt_parcela = models.IntegerField(blank=True, null=True)
    vl_parcela = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    status = models.CharField(max_length=40, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    dt_emprestimo = models.DateField(null=True, blank=True)   
    dt_cobranca = models.DateField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'emp_emprestimos'

class EmprestimoParcela(models.Model):
    id = models.BigAutoField(primary_key=True)    
    nr_parcela = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    dt_vencimento = models.DateField(blank=True, null=True)
    dt_pagamento = models.DateField(blank=True, null=True)
    tp_pagamento = models.CharField(max_length=40, null=True, blank=True)
    status_pagamento = models.CharField(max_length=40, null=True, blank=True)
    vl_parcial = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    emprestimo = models.ForeignKey(Emprestimo, verbose_name='Emprestimo', related_name='EmprestimoParcela', on_delete=models.CASCADE)
    vl_parcela = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qtd_tt_parcelas = models.IntegerField(blank=True, null=True)
    dt_prev_pag_parcial_restante = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'emp_emprestimo_parcelas'