from django.db import models

class Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    # cpf = models.CharField(max_length=11, null=True, blank=True)
    # nome = models.CharField(max_length=150, null=True, blank=True)
    # dt_nascimento = models.DateField(null=True, blank=True)
    # especie = models.CharField(max_length=100, null=True, blank=True)
    # matricula = models.CharField(max_length=20, null=True, blank=True)
    # telefone1 = models.CharField(max_length=20, null=True, blank=True)
    # telefone2 = models.CharField(max_length=20, null=True, blank=True)
    # telefone3 = models.CharField(max_length=20, null=True, blank=True)
    # observacoes = models.TextField(null=True, blank=True)
    # convenio = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'clientes'