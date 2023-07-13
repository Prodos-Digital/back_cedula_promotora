from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, null=True, blank=True)
    cpf_cnpj = models.CharField(max_length=20, null=True, blank=True)
    estado_civil = models.CharField(max_length=20, null=True, blank=True)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    cep = models.CharField(max_length=20, null=True, blank=True)
    logradouro = models.CharField(max_length=255, null=True, blank=True)
    numLogr = models.CharField(max_length=255, null=True, blank=True)
    complLogr = models.CharField(max_length=255, null=True, blank=True)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=10, null=True, blank=True)
