from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.accounts.decorators import htmx_login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import Pacientes
from .forms import PacientesForm


@login_required
def pacientes_view(request):
    pacientes = Pacientes.objects.all().order_by('-created_at')

    return render(request, 'pacientes/pacientes.html',
                  {'pacientes': pacientes}
            )


@login_required
def listar_pacientes_view(request):
    query = request.GET.get('q', '')

    if query:
        pacientes = Pacientes.objects.filter(
            Q(complete_name__icontains=query) | Q(phone_number__icontains=query)
        ) 
    else: 
        pacientes = Pacientes.objects.all()

    return render(request, 'pacientes/partials/listar_pacientes.html',
                  {'pacientes': pacientes}
            )


@login_required
def novo_paciente_view(request):
    if request.method == 'POST':
        form = PacientesForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('pacientes:pacientes')
    else:
        form = PacientesForm()

    return render(request, 'pacientes/novo_paciente.html',
                  {'form': form}
            )


@login_required
def visualizar_paciente_view(request, phone_number):
    paciente = get_object_or_404(Pacientes, phone_number=phone_number)

    if request.method == 'POST':
        form = PacientesForm(request.POST, instance=paciente)

        if form.is_valid():
            form.save()
            return redirect('pacientes:pacientes')

    else:
        form = PacientesForm(instance=paciente)

    return render(request, 'pacientes/visualizar_paciente.html', 
                {'form': form, 'paciente': paciente}
            )


@htmx_login_required
@require_http_methods(['DELETE'])
def deletar_paciente_view(request, phone_number):
    paciente = get_object_or_404(Pacientes, phone_number=phone_number)

    paciente.delete()

    return HttpResponse(status=200)