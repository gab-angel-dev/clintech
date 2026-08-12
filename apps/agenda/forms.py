from django import forms

from .models import Agendamento
from apps.doutores.models import Doutor
from apps.procedimentos.models import Procedimento
from apps.pacientes.models import Pacientes

class AgendamentoForm(forms.ModelForm):

    class Meta:
        model = Agendamento
        fields = [
            "paciente",
            "doutor",
            "procedimento",
            "convenio_utilizado",
            "start_time",
            "end_time",
            "observacoes",
        ]
        widgets = {
            'paciente': forms.HiddenInput(),
            'doutor': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'convenio_utilizado': forms.Select(attrs={'class': 'form-select', 'onchange': '...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        doutor_id = self.data.get("doutor") or self.instance.doutor_id
        paciente_id = self.data.get("paciente") or self.instance.paciente_id

        if not doutor_id:
            self.fields["procedimento"].queryset = Procedimento.objects.none()
            return

        try:
            doutor = Doutor.objects.get(pk=doutor_id, ativo=True)
        except Doutor.DoesNotExist:
            self.fields["procedimento"].queryset = Procedimento.objects.none()
            return

        self.fields["procedimento"].queryset = doutor.procedimentos.filter(ativo=True)

        convenios_doutor = [c.strip().lower() for c in (doutor.convenio or []) if c.strip()]

        if paciente_id:
            try:
                paciente = Pacientes.objects.get(pk=paciente_id)
                convenios_paciente = [
                    c.strip().lower() for c in (paciente.convenio or "").split(",") if c.strip()
                ]
            except Pacientes.DoesNotExist:
                convenios_paciente = []
            # Interseção: só entra na lista se AMBOS aceitarem.
            convenios_disponiveis = [c for c in convenios_doutor if c in convenios_paciente]
        else:
            # Paciente ainda não selecionado — mostra os do doutor por enquanto;
            # o clean() garante que, se o usuário escolher errado, é barrado.
            convenios_disponiveis = convenios_doutor

        convenio_choices = [("", "Particular")] + [
            (c, c.capitalize()) for c in convenios_disponiveis
        ]
        self.fields["convenio_utilizado"].widget = forms.Select(choices=convenio_choices)