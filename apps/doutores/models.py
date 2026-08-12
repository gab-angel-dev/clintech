from django.db import models
from apps.procedimentos.models import Procedimento


class Doutor(models.Model):
    procedimentos = models.ManyToManyField(Procedimento)
    nome = models.CharField(max_length=150, null=False)
    numero = models.CharField(max_length=13, null=False, blank=True)
    calendar_id = models.CharField(max_length=255, null=False)
    ativo = models.BooleanField(default=True, null=False)
    duracao = models.IntegerField(default=30, null=False)
    dias_da_semana = models.JSONField(default=list)
    horario_trabalho = models.JSONField(default=dict)
    convenio = models.JSONField(default=list, blank=True)
    restricao = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'doutores'
        verbose_name = "Doutor"
        verbose_name_plural = "Doutores"