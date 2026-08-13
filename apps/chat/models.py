from django.db import models
from apps.pacientes.models import Pacientes
from django.db.models.functions import Now

class Chat(models.Model):
    session_id = models.ForeignKey(
        Pacientes,
        on_delete=models.CASCADE,
        db_column='session_id',
        to_field='phone_number',
        related_name='mensagens',
    )
    sender = models.CharField(max_length=20, null=True, blank=True)
    agent_name = models.CharField(max_length=50, null=True, blank=True)
    message = models.JSONField()
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        db_table = 'chat'
        indexes = [
            models.Index(fields=['session_id'], name='chat_session_idx'),
        ]

    def __str__(self):
        return f'{self.sender} - {self.session_id_id}'