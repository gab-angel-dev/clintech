from django.db import models
from django.db.models.functions import Now
from apps.doutores.models import Doutor
from apps.procedimentos.models import Procedimento
from apps.pacientes.models import Pacientes
from django.core.exceptions import ValidationError

class StatusAgendamento(models.TextChoices):
    PENDENTE = "pending", "Pendente"
    CONFIRMADO = "confirmed", "Confirmado"
    CANCELADO = "canceled", "Cancelado"


class Agendamento(models.Model):

    paciente = models.ForeignKey(
        Pacientes,
        on_delete=models.SET_NULL,
        null=True,
        related_name="agendamentos",
    )
    doutor = models.ForeignKey(
        Doutor,
        on_delete=models.PROTECT,
        related_name="agendamentos",
    )
    procedimento = models.ForeignKey(
        Procedimento,
        on_delete=models.PROTECT,
        related_name="agendamentos",
    )

    event_id = models.CharField(
        max_length=255,
        unique=True,
    )

    convenio_utilizado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=StatusAgendamento.choices,
        default=StatusAgendamento.PENDENTE,
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    observacoes = models.TextField(blank=True, null=False)

    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'agendamentos'
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["event_id"]),
            models.Index(fields=["start_time"]),
        ]

    def clean(self):
        super().clean()

        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({
                "end_time": "O horário de término deve ser depois do horário de início."
            })

        if not self.convenio_utilizado:
            return

        if not self.paciente_id or not self.doutor_id:
            return
        
        if not self.convenio_utilizado:
            return  # particular — nada a validar

        if not self.paciente_id or not self.doutor_id:
            return  # sem os dois lados, não dá pra validar interseção

        convenio_alvo = self.convenio_utilizado.strip().lower()

        convenios_paciente = [
            c.strip().lower()
            for c in (self.paciente.convenio or "").split(",")
            if c.strip()
        ]
        convenios_doutor = [
            c.strip().lower()
            for c in (self.doutor.convenio or [])
            if c.strip()
        ]

        if convenio_alvo not in convenios_paciente:
            raise ValidationError({
                "convenio_utilizado": (
                    f"O paciente não possui o convênio '{self.convenio_utilizado}' cadastrado."
                )
            })

        if convenio_alvo not in convenios_doutor:
            raise ValidationError({
                "convenio_utilizado": (
                    f"O doutor {self.doutor.nome} não atende pelo convênio '{self.convenio_utilizado}'."
                )
            })

    
    def __str__(self):
        data = self.start_time.strftime("%d/%m/%Y %H:%M")
        return f"{self.procedimento.nome} — {self.doutor.nome} ({data})"

    @property
    def is_cancelavel(self) -> bool:
        return self.status != StatusAgendamento.CANCELADO

    