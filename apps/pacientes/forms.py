from django import forms
from .models import Pacientes

class PacientesForm(forms.ModelForm):
    class Meta:
        model = Pacientes
        exclude = ['metadata']
        labels = {
            'phone_number': 'Número de Contato',
            'complete_name': 'Nome',
            'require_human': 'Humano Ativo',
            'complete_register': 'Cadastro Completo',
            'origin_contact': 'Plataforma de Origem',
            'convenio': 'Convênio',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'DDD + DDI  Ex: 557999999999'}),
            'complete_name': forms.TextInput(attrs={'placeholder': 'Nome do Paciente'}),
            'cpf': forms.TextInput(attrs={'placeholder': 'Apenas números  Ex: 00011122233'}),
            'convenio': forms.TextInput(attrs={'placeholder': 'Ex: unimed'})
        }