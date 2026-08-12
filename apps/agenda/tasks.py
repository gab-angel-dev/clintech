# apps/agenda/tasks.py

import logging

from celery import shared_task
from django.utils import timezone
from apps.chat.evo import EvolutionAPI
from apps.chat.models import Chat
from .models import Agendamento, StatusAgendamento

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def enviar_lembrete_consulta_task(agendamento_id: int) -> None:
    try:
        agendamento = Agendamento.objects.select_related(
            "paciente", "doutor", "procedimento"
        ).get(pk=agendamento_id)
    except Agendamento.DoesNotExist:
        logger.warning("Lembrete não enviado: Agendamento %s não existe mais.", agendamento_id)
        return

    if agendamento.status == StatusAgendamento.CANCELADO:
        logger.info("Lembrete não enviado: Agendamento %s foi cancelado.", agendamento_id)
        return

    if not agendamento.paciente:
        logger.warning("Lembrete não enviado: paciente do Agendamento %s foi removido.", agendamento_id)
        return

    inicio = timezone.localtime(agendamento.start_time)
    agora = timezone.localtime(timezone.now())

    mensagem = (
        f"{'Bom dia' if agora.hour < 12 else 'Boa tarde'}, {agendamento.paciente.complete_name}! "
        f"Passando pra lembrar que sua consulta de {agendamento.procedimento.nome} "
        f"está marcada para amanhã dia {inicio.strftime('%d/%m')} às {inicio.strftime('%H:%M')} "
        f"com {agendamento.doutor.nome}. Posso confirmar?"
    )

    Chat.objects.create(
        session_id=agendamento.paciente,
        sender="ai",
        agent_name="lembrete",
        message={"type": "ai", "content": mensagem},
    )

    evo = EvolutionAPI()
    evo.sender_text(number=agendamento.paciente.phone_number, text=mensagem)

