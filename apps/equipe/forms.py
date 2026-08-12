from django import forms
from apps.accounts.models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class AdminCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class AdminEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']