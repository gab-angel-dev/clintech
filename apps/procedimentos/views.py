from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Procedimento
from .forms import PrcedimentoForm

@login_required
def procedimentos_view(request):
    procedimentos = Procedimento.objects.all().order_by('-created_at')
    return render(request, 'procedimentos/procedimentos.html',
            {'procedimentos': procedimentos}
    )


@login_required
def novo_procedimento_view(request):
    if request.method == "POST":
        form = PrcedimentoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('procedimentos:procedimentos')
    else:
        form = PrcedimentoForm()

    return render(request, 'procedimentos/novo_procedimento.html', 
            {'form': form}
    )


@login_required
def visualizar_procedimento_view(request, pk):
    procedimento = get_object_or_404(Procedimento, pk=pk)

    if request.method == "POST":
        form = PrcedimentoForm(request.POST, instance=procedimento)

        if form.is_valid():
            form.save()
            return redirect('procedimentos:procedimentos')
    else:
        form = PrcedimentoForm(instance=procedimento)

    return render(request, 'procedimentos/novo_procedimento.html', 
            {'form': form}
    )