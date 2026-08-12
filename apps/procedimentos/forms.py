from django import forms
from .models import Procedimento

class PrcedimentoForm(forms.ModelForm):
    
    class Meta:
        model = Procedimento
        fields = '__all__'
        labels = {
            'valor_padrao': 'Valor Padrão',
            'descricao': 'Descrição',
            'duracao_minuto': 'Duração em Minutos',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do procedimento'}),
            'triagem': forms.TextInput(attrs={'placeholder': 'Digite a triagem que precisa ser feita para realizar esse procedimento, se houver'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Descrição do procedimento'})
        }