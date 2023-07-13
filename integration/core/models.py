from django.db import models


class Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    cpf = models.CharField(max_length=11)
    nome = models.CharField(max_length=150)
    dt_nascimento = models.DateField(null=True, blank=True)
    especie = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20)
    telefone1 = models.CharField(max_length=20)
    telefone2 = models.CharField(max_length=20)
    telefone3 = models.CharField(max_length=20)
    observacoes = models.TextField()

    def __str__(self):
        return self.nome
