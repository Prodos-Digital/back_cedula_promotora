from django.db import models


class Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    nome = models.CharField(max_length=150, null=True, blank=True)
    dt_nascimento = models.DateField(null=True, blank=True)
    especie = models.CharField(max_length=100, null=True, blank=True)
    matricula = models.CharField(max_length=20, null=True, blank=True)
    telefone1 = models.CharField(max_length=20, null=True, blank=True)
    telefone2 = models.CharField(max_length=20, null=True, blank=True)
    telefone3 = models.CharField(max_length=20, null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

class Contrato(models.Model):
    id = models.BigAutoField(primary_key=True)
    promotora = models.CharField(max_length=255, null=True, blank=True)
    dt_digitacao = models.DateTimeField(null=True, blank=True)
    nr_contrato = models.CharField(max_length=255, null=True, blank=True)
    no_cliente = models.CharField(max_length=255, null=True, blank=True)
    cpf = models.CharField(max_length=255, null=True, blank=True)
    convenio = models.CharField(max_length=255, null=True, blank=True)
    operacao = models.CharField(max_length=255, null=True, blank=True)
    banco = models.CharField(max_length=255, null=True, blank=True)
    vl_contrato = models.FloatField(null=True, blank=True)
    qt_parcelas = models.CharField(max_length=255, null=True, blank=True)
    vl_parcela = models.CharField(max_length=255, null=True, blank=True)
    dt_pag_cliente = models.DateTimeField(null=True, blank=True)
    dt_pag_comissao = models.CharField(max_length=255, null=True, blank=True)
    vl_comissao = models.FloatField(null=True, blank=True)
    porcentagem = models.FloatField(null=True, blank=True)
    corretor = models.CharField(max_length=255, null=True, blank=True)
