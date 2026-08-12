from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import DoutoresForm
from .models import Doutor


DIAS_SEMANA_EXIBICAO = [
    (7, 'Dom'),
    (1, 'Seg'),
    (2, 'Ter'),
    (3, 'Qua'),
    (4, 'Qui'),
    (5, 'Sex'),
    (6, 'Sáb'),
]

@login_required
def doutores_view(request):
    doutores = Doutor.objects.all().order_by('-created_at')
    return render(request, 'doutores/doutores.html',
                  {'doutores': doutores, 'dias_semana_exibicao': DIAS_SEMANA_EXIBICAO})



@login_required
def novo_doutor_view(request):
    if request.method == 'POST':
        form = DoutoresForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('doutores:doutores')
    else:
        form = DoutoresForm()

    return render(request, 'doutores/novo_doutor.html',
                {'form': form}
            )


@login_required
def visualizar_doutor_view(request, pk):
    doutor = get_object_or_404(Doutor, pk=pk)

    if request.method == 'POST':
        form = DoutoresForm(request.POST, instance=doutor)
        if form.is_valid():
            form.save()

        return redirect('doutores:doutores')

    else:
        form = DoutoresForm(instance=doutor)

    return render(request, 'doutores/novo_doutor.html',
                {'form': form}
            )

@login_required
@require_POST
def toggle_ativo_view(request, pk):
    doutor = get_object_or_404(Doutor, pk=pk)
    doutor.ativo = not doutor.ativo
    doutor.save()

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'doutores/partials/doutor_card.html',
                      {'doutor': doutor, 'dias_semana_exibicao': DIAS_SEMANA_EXIBICAO})

    return redirect('doutores:doutores')