from django.db import models
from django.db.models.functions import Now
from apps.pacientes.models import Pacientes


class TokenUsage(models.Model):
    paciente = models.ForeignKey(
        Pacientes,
        on_delete=models.SET_NULL,
        to_field="phone_number",
        null=True,
        related_name="usos_de_token",
    )
    message_id = models.TextField(null=True, blank=True)
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField()
    total_tokens = models.IntegerField()
    model_name = models.CharField(max_length=200, null=True, blank=True)
    provider = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = "token_usage"
        verbose_name = "Uso de Token"
        verbose_name_plural = "Usos de Token"

    def __str__(self):
        nome = self.paciente.complete_name if self.paciente else "Paciente removido"
        return f"{nome} — {self.total_tokens} tokens ({self.model_name})"