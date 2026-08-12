from django.db import models
from decimal import Decimal

class Procedimento(models.Model):
    nome = models.CharField(max_length=150)
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    triagem = models.TextField(null=False, blank=True)
    descricao = models.TextField()
    duracao_minuto = models.IntegerField(default=30, null=False)
    ativo = models.BooleanField(default=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'procedimentos'
