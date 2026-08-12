from django import forms
from .models import Arquivo, Embedding


class ArquivoForm(forms.ModelForm):
    class Meta:
        model = Arquivo
        fields = "__all__"