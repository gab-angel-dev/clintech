from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.accounts.decorators import htmx_login_required
from apps.pacientes.models import Pacientes
from django.db.models import Q
from django.http import HttpResponse
from .models import Chat
from .tasks import enviar_msg_evo_task


@login_required
def chat_view(request):
    pacientes_com_conversa = Pacientes.objects.filter(mensagens__isnull=False).distinct()
    return render(request, 'chat/chat.html', {'pacientes': pacientes_com_conversa})

@login_required
def chat_conversa_view(request, phone_number):
    paciente_selecionado = get_object_or_404(Pacientes, phone_number=phone_number)
    pacientes = Pacientes.objects.filter(mensagens__isnull=False).distinct()
    mensagens = paciente_selecionado.mensagens.order_by('created_at')

    return render(request, 'chat/chat.html', {
        'pacientes': pacientes,
        'paciente_selecionado': paciente_selecionado,
        'mensagens': mensagens,
    })


@login_required
def chat_buscar_pacientes_view(request):
    query = request.GET.get('q', '')
    pacientes = Pacientes.objects.filter(mensagens__isnull=False).distinct()

    if query:
        pacientes = pacientes.filter(
            Q(complete_name__icontains=query) | Q(phone_number__icontains=query)
        )

    return render(request, 'chat/partials/lista_conversas.html', {'pacientes': pacientes})


@login_required
def chat_enviar_mensagem_view(request, phone_number):
    paciente = get_object_or_404(Pacientes, phone_number=phone_number)

    if not paciente.require_human:
        return HttpResponse(status=403)

    if request.method == 'POST':
        texto = request.POST.get('mensagem', '').strip()

        if texto:
            mensagem = Chat.objects.create(
                session_id=paciente,
                sender='ai',
                agent_name=None,
                message={'type': 'ai', 'content': texto},
            )

            enviar_msg_evo_task.delay(numero=paciente.phone_number, mensagem=texto)

            # Reaproveita o mesmo partial do polling — ele já inclui o
            # marcador hx-swap-oob, então o próximo ciclo de polling
            # já sabe que essa mensagem foi mostrada e não busca de novo.
            return render(request, 'chat/partials/novas_mensagens.html', {
                'mensagens': [mensagem],
            })

    return HttpResponse(status=204)


@login_required
@require_http_methods(['POST'])
def chat_toggle_atendimento_view(request, phone_number):
    paciente = get_object_or_404(Pacientes, phone_number=phone_number)
    paciente.require_human = not paciente.require_human
    paciente.save(update_fields=['require_human'])

    return render(request, 'chat/partials/input_mensagem.html', {'paciente_selecionado': paciente})


@login_required
def chat_novas_mensagens_view(request, phone_number):
    paciente = get_object_or_404(Pacientes, phone_number=phone_number)
    ultima_id = request.GET.get('ultima_id', 0)

    novas_mensagens = paciente.mensagens.filter(id__gt=ultima_id).order_by('created_at')

    if not novas_mensagens.exists():
        return HttpResponse(status=204)

    return render(request, 'chat/partials/novas_mensagens.html', {
        'mensagens': novas_mensagens,
    })