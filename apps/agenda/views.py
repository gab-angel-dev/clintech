import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.accounts.decorators import htmx_login_required
from .google_calendar import (
    adicionar_evento,
    deletar_evento,
    verificar_disponibilidade,
)

from datetime import datetime

from apps.doutores.models import Doutor
from .forms import AgendamentoForm
from .models import Agendamento, StatusAgendamento
from django.db.models import Q
from apps.pacientes.models import Pacientes
from .tasks import enviar_lembrete_consulta_task
from apps.chat.tasks import enviar_msg_evo_task 

logger = logging.getLogger(__name__)


# ── Listagem / calendário ────────────────────────────────────────────────────

@login_required
def agenda_list(request):
    from apps.doutores.models import Doutor

    doutores = Doutor.objects.filter(ativo=True).order_by("nome")
    return render(request, "agenda/agenda_list.html", {"doutores": doutores})


@htmx_login_required
def agenda_events(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    doutor_id = request.GET.get("doutor", "")

    qs = Agendamento.objects.select_related("paciente", "doutor", "procedimento")

    if start:
        qs = qs.filter(start_time__date__gte=start)
    if end:
        qs = qs.filter(start_time__date__lte=end)
    if doutor_id:
        qs = qs.filter(doutor_id=doutor_id)

    events = []
    for ag in qs:
        paciente_nome = ag.paciente.complete_name if ag.paciente else "Paciente removido"

        events.append({
            "id": ag.event_id,
            "title": f"{paciente_nome} — {ag.procedimento.nome}",
            "start": ag.start_time.isoformat(),
            "end": ag.end_time.isoformat(),
            "extendedProps": {
                "db_id": ag.id,
                "event_id": ag.event_id,
                "paciente_id": ag.paciente_id,
                "patient_name": paciente_nome,
                "convenio": ag.convenio_utilizado,
                "dr_responsible": ag.doutor.nome,
                "doutor_id": ag.doutor_id,
                "procedure": ag.procedimento.nome,
                "description": ag.observacoes,
                "status": ag.status,
                "start_time": ag.start_time.isoformat(),
                "end_time": ag.end_time.isoformat(),
            },
        })

    return JsonResponse(events, safe=False)


# ── Disponibilidade (HTMX) ───────────────────────────────────────────────────

@htmx_login_required
def agenda_availability(request):
    doutor_id = request.GET.get("doutor", "")
    start_time = request.GET.get("start_time", "")
    end_time = request.GET.get("end_time", "")

    if not all([doutor_id, start_time, end_time]):
        return render(request, "agenda/partials/_availability_result.html", {
            "error": "Selecione doutor, início e fim antes de verificar.",
        })

    try:
        doutor = Doutor.objects.get(pk=doutor_id)
    except Doutor.DoesNotExist:
        return render(request, "agenda/partials/_availability_result.html", {
            "error": "Doutor inválido.",
        })

    try:
        aware_start = timezone.make_aware(datetime.strptime(start_time, "%Y-%m-%dT%H:%M"))
        aware_end = timezone.make_aware(datetime.strptime(end_time, "%Y-%m-%dT%H:%M"))

        result = verificar_disponibilidade(
            doutor.calendar_id,
            aware_start.isoformat(),
            aware_end.isoformat(),
        )
        return render(request, "agenda/partials/_availability_result.html", {
            "available": result.get("available"),
            "conflict": result.get("conflict"),
        })

    except EnvironmentError as e:
        logger.error("Configuração do Google Calendar ausente: %s", e)
        return render(request, "agenda/partials/_availability_result.html", {
            "error": "Serviço de agenda temporariamente indisponível. Contate o suporte.",
        })
    except (ValueError, TypeError) as e:
        logger.warning("Parâmetros inválidos ao verificar disponibilidade: %s", e)
        return render(request, "agenda/partials/_availability_result.html", {
            "error": "Data ou horário inválido.",
        })
    except Exception as e:
        logger.error("Erro inesperado na verificação de disponibilidade: %s", e)
        return render(request, "agenda/partials/_availability_result.html", {
            "error": "Não foi possível verificar a disponibilidade. Tente novamente.",
        })


# ── Criação (form único) ──────────────────────────────────────────────────────

@login_required
def agenda_create(request):
    is_htmx = request.headers.get("HX-Request") == "true"

    if request.method == "POST":
        form = AgendamentoForm(request.POST)

        if not form.is_valid():
            return render(request, "agenda/partials/_form.html", {"form": form}, status=422)

        agendamento = form.save(commit=False)
        summary = f"{agendamento.procedimento.nome} — {agendamento.doutor.nome}"

        try:
            gc_event = adicionar_evento(
                calendar_id=agendamento.doutor.calendar_id,
                summary=summary,
                start_time=agendamento.start_time.isoformat(),
                end_time=agendamento.end_time.isoformat(),
                description=agendamento.observacoes,
            )
        except EnvironmentError as e:
            logger.error("Configuração do Google Calendar ausente: %s", e)
            return render(request, "agenda/partials/_step_error.html", {
                "error": "Serviço de agenda indisponível no momento. Contate o suporte.",
            }, status=503)
        except Exception as e:
            logger.error("Erro ao criar evento no Google Calendar: %s", e)
            return render(request, "agenda/partials/_step_error.html", {
                "error": "Não foi possível criar o evento na agenda. Tente novamente.",
            }, status=502)

        try:
            with transaction.atomic():
                agendamento.event_id = gc_event["id"]
                agendamento.status = StatusAgendamento.PENDENTE
                agendamento.full_clean()
                agendamento.save()
        except ValidationError as e:
            logger.warning("Agendamento rejeitado na validação: %s", e)
            try:
                deletar_evento(agendamento.doutor.calendar_id, gc_event["id"])
            except Exception as cleanup_error:
                logger.error("Falha ao reverter evento no Calendar após validação: %s", cleanup_error)
            return render(request, "agenda/partials/_form.html", {
                "form": form,
                "erro_negocio": e.messages,
            }, status=422)

        # Normaliza UMA VEZ SÓ — o formulário sempre entrega naive, e o .save()
        # não altera o objeto em memória. Reaproveitamos essas duas variáveis
        # no resto da função (lembrete + mensagem ao doutor), sem repetir a
        # conversão nem arriscar esquecer dela em algum ponto novo no futuro.
        # ── Efeitos colaterais não essenciais ────────────────────────────────
# Se algo aqui falhar, o agendamento JÁ FOI criado com sucesso no
# Calendar e no banco — não deixamos essa falha virar erro 500 pro
# usuário, só logamos e seguimos.
        try:
            inicio_aware = (
                timezone.make_aware(agendamento.start_time)
                if timezone.is_naive(agendamento.start_time)
                else agendamento.start_time
            )
            fim_aware = (
                timezone.make_aware(agendamento.end_time)
                if timezone.is_naive(agendamento.end_time)
                else agendamento.end_time
            )

            lembrete_eta = inicio_aware - timedelta(hours=1)
            if lembrete_eta > timezone.now():
                enviar_lembrete_consulta_task.apply_async(args=[agendamento.id], eta=lembrete_eta)

            nome_paciente = agendamento.paciente.complete_name if agendamento.paciente else "Paciente"

            mensagem_doutor = (
                f"🔔 Novo agendamento\n\n"
                f"👤 Paciente: {nome_paciente}\n"
                f"📞 Telefone: {agendamento.paciente.phone_number if agendamento.paciente else '—'}\n"
                f"📅 Data: {inicio_aware.strftime('%d/%m/%Y')}\n"
                f"🕐 Horário: {inicio_aware.strftime('%H:%M')} às {fim_aware.strftime('%H:%M')}\n"
                f"Convênio: {agendamento.convenio_utilizado or 'Particular'}\n"
                f"Procedimento: {agendamento.procedimento.nome}\n"
                f"Observações: {agendamento.observacoes or '—'}\n\n"
                f"Verifique a agenda ou entre em contato."
            )
            enviar_msg_evo_task.delay(agendamento.doutor.numero, mensagem_doutor)

        except Exception as e:
            logger.error(
                "Agendamento %s criado com sucesso, mas falha ao agendar lembrete/notificação: %s",
                agendamento.id, e,
            )

        return render(request, "agenda/partials/_step_success.html", {"agendamento": agendamento})

    # GET
    form = AgendamentoForm()
    if is_htmx:
        return render(request, "agenda/partials/_form.html", {"form": form})
    return render(request, "agenda/agenda_form.html", {"form": form})


# ── Cancelamento ──────────────────────────────────────────────────────────────

@htmx_login_required
def agenda_cancel(request, event_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)

    agendamento = get_object_or_404(
        Agendamento.objects.select_related("doutor", "paciente", "procedimento"),
        event_id=event_id,
    )

    if agendamento.status == StatusAgendamento.CANCELADO:
        return render(request, "agenda/partials/_step_error.html", {
            "error": "Este agendamento já estava cancelado.",
        }, status=409)

    try:
        deletar_evento(agendamento.doutor.calendar_id, event_id)
    except Exception as e:
        logger.error("Erro ao deletar evento %s do Google Calendar: %s", event_id, e)
        return render(request, "agenda/partials/_step_error.html", {
            "error": "Não foi possível cancelar na agenda externa. Tente novamente.",
        }, status=502)

    agendamento.status = StatusAgendamento.CANCELADO
    agendamento.save(update_fields=["status", "updated_at"])

    nome_paciente = agendamento.paciente.complete_name if agendamento.paciente else "Paciente"
    start = timezone.localtime(agendamento.start_time)
    end = timezone.localtime(agendamento.end_time)

    mensagem_doutor = (
        f"❌ Consulta cancelada\n\n"
        f"👤 Paciente: {nome_paciente}\n"
        f"📞 Telefone: {agendamento.paciente.phone_number}\n"
        f"📅 Data: {start.strftime('%d/%m/%Y')}\n"
        f"🕐 Horário: {start.strftime('%H:%M')} às {end.strftime('%H:%M')}\n"
        f"Convênio: {agendamento.convenio_utilizado}\n"
        f"Procedimento: {agendamento.procedimento or '—'}\n"
        f"Observações: {agendamento.observacoes or '—'}\n\n"
        f"Verifique a agenda ou entre em contato."
    )
    
    enviar_msg_evo_task.delay(agendamento.doutor.numero, mensagem_doutor)

    return render(request, "agenda/partials/_cancel_success.html", {"agendamento": agendamento})


@htmx_login_required
def agenda_event_detail(request, event_id):
    agendamento = get_object_or_404(
        Agendamento.objects.select_related("paciente", "doutor", "procedimento"),
        event_id=event_id,
    )
    return render(request, "agenda/partials/_event_detail.html", {"agendamento": agendamento})


@htmx_login_required
def agenda_procedimento_convenio(request):
    """Fragmento HTMX disparado ao trocar o doutor no form de criação."""
    form = AgendamentoForm(data=request.GET or None)
    return render(request, "agenda/partials/_procedimento_convenio.html", {"form": form})

@htmx_login_required
def agenda_patient_search(request):
    q = (request.GET.get("q") or "").strip()

    if len(q) < 2:
        return render(request, "agenda/partials/_patient_results.html", {"pacientes": []})

    pacientes = Pacientes.objects.filter(
        Q(complete_name__icontains=q) | Q(phone_number__icontains=q)
    ).order_by("complete_name")[:10]

    return render(request, "agenda/partials/_patient_results.html", {"pacientes": pacientes})