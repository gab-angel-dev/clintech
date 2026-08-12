from django import forms
from .models import Doutor
from django import forms
from django.db.models import Q
from .models import Doutor
from apps.procedimentos.models import Procedimento


class ProcedimentoMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if not obj.ativo:
            return f"{obj.nome} (inativo)"
        return obj.nome


class DoutoresForm(forms.ModelForm):

    # ========== DIAS DA SEMANA ======================================================

    DIAS_SEMANA_CHOICE = [
        (1, 'Segunda'),
        (2, 'Terça'),
        (3, 'Quarta'),
        (4, 'Quinta'),
        (5, 'Sexta'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]

    dias_da_semana = forms.MultipleChoiceField(
        choices=DIAS_SEMANA_CHOICE,
        widget=forms.CheckboxSelectMultiple,
        label='Dias da Semana',
        required=False
    )

    def clean_dias_da_semana(self):
        dias = self.cleaned_data['dias_da_semana']
        return [int(dia) for dia in dias]


    # ========== NOME ======================================================
    

    
    # ========== HORARIO DE TRABALHO ======================================================

    manha_inicio = forms.TimeField(
        required=False,
        label='Horário de início',
        input_formats=['%H:%M'],
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
    manha_fim = forms.TimeField(
        label='Horário de fim',
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
    tarde_inicio = forms.TimeField(
        label='Horário de início',
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
    tarde_fim = forms.TimeField(
        label='Horário de fim',
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'})
    )
    

    def clean(self):
        cleaned_data = super().clean()

        manha_inicio = cleaned_data.get('manha_inicio')
        manha_fim = cleaned_data.get('manha_fim')
        tarde_inicio = cleaned_data.get('tarde_inicio')
        tarde_fim = cleaned_data.get('tarde_fim')

        horario_trabalho = {}

        if manha_inicio and manha_fim:
            horario_trabalho['manha'] = {
                'inicio': manha_inicio.strftime('%H:%M'),
                'fim': manha_fim.strftime('%H:%M')
            }

        if tarde_inicio and tarde_fim:
            horario_trabalho['tarde'] = {
                'inicio': tarde_inicio.strftime('%H:%M'),
                'fim': tarde_fim.strftime('%H:%M')
            }

        cleaned_data['horario_trabalho'] = horario_trabalho
        return cleaned_data

    #  ========== CONVENIO ======================================================

    convenio = forms.CharField(
        required=False,
        label='Convênios Aceitos',
        widget=forms.TextInput(attrs={'placeholder': 'Ex: unimed, bradesco, petrobrás'})
    )

    def clean_convenio(self):
        texto = self.cleaned_data['convenio'].split(',')
        convenios = [convenio.strip().lower() for convenio in texto]
        return convenios



    def save(self, commit=True):
        doutor = super().save(commit=False)
        doutor.horario_trabalho = self.cleaned_data.get('horario_trabalho', {})

        if commit:
            doutor.save()
            self.save_m2m()

        return doutor

    #  ========== RESTRICOES ======================================================

    restricao = forms.CharField(
        required=False,
        label='Restrição',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Uma restrição por linha, no formato chave: valor\nEx: pagamento: apenas cartão de crédito',
        }),
    )

    def clean_restricao(self):
        texto = self.cleaned_data.get('restricao', '')
        restricoes = {}

        for linha in texto.split('\n'):
            linha = linha.strip()
            if not linha:
                continue

            if ':' not in linha:
                raise forms.ValidationError(
                    f'A linha "{linha}" está fora do formato esperado (chave: valor).'
                )

            chave, valor = linha.split(':', maxsplit=1)
            restricoes[chave.strip()] = valor.strip()

        return restricoes

    procedimentos = ProcedimentoMultipleChoiceField(
        queryset=Procedimento.objects.none(),  
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if self.instance and self.instance.pk:
                # Edição: mostra ativos + os que esse doutor já tinha vinculados,
                # mesmo que tenham sido desativados depois — evita que o save()
                # remova silenciosamente um vínculo antigo só porque a opção
                # sumiu da lista.
                vinculados_atuais = self.instance.procedimentos.values_list("pk", flat=True)
                self.fields["procedimentos"].queryset = Procedimento.objects.filter(
                    Q(ativo=True) | Q(pk__in=vinculados_atuais)
                )

                # Convênio: lista → string separada por vírgula
                self.initial['convenio'] = ', '.join(self.instance.convenio or [])

                # Horário de trabalho: dict aninhado → 4 campos separados
                horario = self.instance.horario_trabalho or {}
                manha = horario.get('manha', {})
                tarde = horario.get('tarde', {})

                self.initial['manha_inicio'] = manha.get('inicio')
                self.initial['manha_fim'] = manha.get('fim')
                self.initial['tarde_inicio'] = tarde.get('inicio')
                self.initial['tarde_fim'] = tarde.get('fim')

                self.initial['restricao'] = '\n'.join(
                    f'{chave}: {valor}' for chave, valor in (self.instance.restricao or {}).items()
                )
            else:
                # Criação: só procedimentos ativos podem ser escolhidos.
                self.fields["procedimentos"].queryset = Procedimento.objects.filter(ativo=True)

        
    class Meta:
        model = Doutor
        exclude = ['horario_trabalho']
        widgets = {
            'procedimentos': forms.CheckboxSelectMultiple(),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Dra. Ana Souza'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DDD + DDI  Ex: 557999999999'}),
            'calendar_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID da agenda do Google Calendário'}),
        }
        labels = {
            'nome': 'Nome',
            'numero': 'Número de Contato',
            'calendar_id': 'ID da Agenda',
            'ativo': 'Doutor Ativo',
            'duracao': 'Duração Padrão de uma Consulta (min)',
            'procedimentos': 'Procedimentos Atendidos',
        }