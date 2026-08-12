from django.db import models

class Pacientes(models.Model):
    phone_number = models.CharField(primary_key=True, max_length=13, null=False, verbose_name='Número de Contato')
    complete_name = models.CharField(max_length=150, null=False, blank=True)
    require_human  = models.BooleanField(default=False, null=False)
    complete_register = models.BooleanField(default=False, null=False)
    origin_contact = models.TextField(default='whatsapp', null=False)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    convenio = models.TextField(null=False, blank=True)
    metadata = models.JSONField(default=dict, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pacientes'
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
