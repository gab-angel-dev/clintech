from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from .forms import RegistrationForm


def cadastro_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("accounts:login")
    else:
        form = RegistrationForm()
        
    return render(request, "accounts/cadastro.html", {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home:metricas')
        else:
            return render(request, 'accounts/login.html', {'error': 'Usuário ou senha inválidos'})

    return render(request, 'accounts/login.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('accounts:login')