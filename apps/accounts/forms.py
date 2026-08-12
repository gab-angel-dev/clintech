from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-input', 'placeholder': 'seu@email.com'})
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Digite seu nome'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': '••••••'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': '••••••'})

        