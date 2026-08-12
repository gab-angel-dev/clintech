from celery import shared_task
from .evo import EvolutionAPI
from apps.chat.models import Chat


@shared_task
def enviar_msg_evo_task(numero: str, mensagem: str):
    evo = EvolutionAPI()

    return  evo.sender_text(
                number=numero,
                text=mensagem
            )

