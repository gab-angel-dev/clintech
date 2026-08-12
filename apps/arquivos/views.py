from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.accounts.decorators import htmx_login_required
from django.http import HttpResponse
from .models import Arquivo, Embedding
from .forms import ArquivoForm
from .tasks import gerar_embeddings_task

#   ============= ARQUIVOS =================================================
@login_required
def arquivos_view(request):
    arquivos = Arquivo.objects.all().order_by('-created_at')

    return render(request, 'arquivos/arquivos.html',
            {'arquivos': arquivos}
    )


@login_required
def arquivo_novo_view(request):
    arquivos = Arquivo.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = ArquivoForm(request.POST, request.FILES)

        if form.is_valid():
            arquivo = form.save()

            gerar_embeddings_task.delay(arquivo.id)

            return render(request, 'arquivos/arquivos.html',
                    {'response': "Os embeddings estão sendo gerados...",
                        'arquivos': arquivos
                     }
            )
    else:
        form = ArquivoForm()

    return render(request, 'arquivos/arquivo_novo.html', 
            {'form': form}
    )


@htmx_login_required
@require_http_methods(['DELETE'])
def arquivo_deletar_view(request, pk):
    arquivo = get_object_or_404(Arquivo, pk=pk)
    arquivo.arquivo.delete(save=False)
    arquivo.delete()

    return HttpResponse(status=200)


# =============== EMBEDDINGS =================================================
@login_required
def embedding_view(request):
    embeddings = Embedding.objects.all().order_by('-created_at')

    return render(request, 'arquivos/embeddings.html',
            {'embeddings': embeddings}
    )


@login_required
def embedding_info_view(request, pk):
    embedding = get_object_or_404(Embedding, pk=pk)

    return render(request, 'arquivos/embedding_info.html',
            {'embedding': embedding}
    )