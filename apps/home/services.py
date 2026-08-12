from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from apps.agenda.models import Agendamento
from apps.chat.models import Chat
from apps.doutores.models import Doutor
from apps.pacientes.models import Pacientes
from django.db.models import Count, Sum

from .costs import calcular_custo, normalizar_model_name
from .models import TokenUsage


# ========= METRICAS ========================================================================================================

def get_summary(start, end):
    total_mensagens = Chat.objects.filter(
        created_at__date__gte=start, created_at__date__lte=end
    ).count()

    total_usuarios = Pacientes.objects.filter(
        created_at__date__gte=start, created_at__date__lte=end
    ).count()

    total_agendamentos = Agendamento.objects.filter(
        created_at__date__gte=start, created_at__date__lte=end
    ).count()

    total_conversas = (
        Chat.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("session_id").distinct().count()
    )

    media_msg_conversa = round(total_mensagens / total_conversas, 1) if total_conversas else 0

    return {
        "total_mensagens": total_mensagens,
        "total_usuarios": total_usuarios,
        "total_agendamentos": total_agendamentos,
        "media_msg_conversa": media_msg_conversa,
    }


def get_appointments_by_month():
    dados = (
        Agendamento.objects
        .annotate(mes=TruncMonth("start_time"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("-mes")[:6]
    )
    dados = list(reversed(list(dados)))
    return [{"mes": d["mes"].strftime("%m/%Y"), "total": d["total"]} for d in dados]


def get_messages_by_day(start, end):
    dados = (
        Chat.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("created_at__date", "sender")
        .annotate(total=Count("id"))
        .order_by("created_at__date")
    )

    por_dia = {}
    for item in dados:
        dia = item["created_at__date"].strftime("%d/%m")
        por_dia.setdefault(dia, {"human": 0, "ai": 0})
        if item["sender"] in por_dia[dia]:
            por_dia[dia][item["sender"]] = item["total"]

    return [{"dia": d, "usuario": v["human"], "ia": v["ai"]} for d, v in por_dia.items()]


def get_procedures_distribution(start, end):
    dados = list(
        Agendamento.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("procedimento__nome")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    top6 = dados[:6]
    outros_total = sum(item["total"] for item in dados[6:])

    resultado = [
        {"procedimento": item["procedimento__nome"] or "Não informado", "total": item["total"]}
        for item in top6
    ]
    if outros_total:
        resultado.append({"procedimento": "Outros", "total": outros_total})
    return resultado


def get_doctors_ranking(start, end):
    return list(
        Doutor.objects
        .filter(ativo=True)
        .annotate(
            total_agendamentos=Count(
                "agendamentos",
                filter=Q(
                    agendamentos__created_at__date__gte=start,
                    agendamentos__created_at__date__lte=end,
                ),
            )
        )
        .order_by("-total_agendamentos")
    )


def get_appointments_list(start, end):
    return (
        Agendamento.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .select_related("paciente", "doutor", "procedimento")
        .order_by("start_time")
    )


# ========= CUSTOS ========================================================================================================


def get_costs_summary(start, end, taxa_cambio):
    qs = TokenUsage.objects.filter(created_at__date__gte=start, created_at__date__lte=end)

    agregados = qs.aggregate(
        total_tokens=Sum("total_tokens"),
        input_tokens=Sum("input_tokens"),
        output_tokens=Sum("output_tokens"),
    )

    custo_usd = 0.0
    por_modelo = qs.values("model_name").annotate(
        input_tokens=Sum("input_tokens"), output_tokens=Sum("output_tokens")
    )
    for item in por_modelo:
        custo_usd += calcular_custo(
            item["input_tokens"] or 0, item["output_tokens"] or 0, item["model_name"]
        )

    return {
        "total_tokens": agregados["total_tokens"] or 0,
        "input_tokens": agregados["input_tokens"] or 0,
        "output_tokens": agregados["output_tokens"] or 0,
        "estimated_cost_usd": round(custo_usd, 4),
        "estimated_cost_brl": round(custo_usd * taxa_cambio, 2),
        "exchange_rate": taxa_cambio,
    }


def get_tokens_by_day(start, end):
    dados = (
        TokenUsage.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("created_at__date")
        .annotate(entrada=Sum("input_tokens"), saida=Sum("output_tokens"))
        .order_by("created_at__date")
    )
    return [
        {"dia": d["created_at__date"].strftime("%d/%m"), "entrada": d["entrada"] or 0, "saida": d["saida"] or 0}
        for d in dados
    ]


def get_cost_by_day(start, end):
    dados = (
        TokenUsage.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("created_at__date", "model_name")
        .annotate(input_tokens=Sum("input_tokens"), output_tokens=Sum("output_tokens"))
        .order_by("created_at__date")
    )

    custo_por_dia = {}
    for item in dados:
        dia = item["created_at__date"].strftime("%d/%m")
        custo = calcular_custo(item["input_tokens"] or 0, item["output_tokens"] or 0, item["model_name"])
        custo_por_dia[dia] = custo_por_dia.get(dia, 0) + custo

    return [{"dia": dia, "custo": round(custo, 4)} for dia, custo in custo_por_dia.items()]



def get_costs_by_model(start, end):
    dados = (
        TokenUsage.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("model_name")
        .annotate(total=Sum("total_tokens"))
    )

    agrupado = {}
    for item in dados:
        nome = normalizar_model_name(item["model_name"]) or "Desconhecido"
        agrupado[nome] = agrupado.get(nome, 0) + (item["total"] or 0)

    resultado = [{"modelo": nome, "total": total} for nome, total in agrupado.items()]
    return sorted(resultado, key=lambda x: -x["total"])


def get_costs_by_user(start, end):
    return list(
        TokenUsage.objects
        .filter(created_at__date__gte=start, created_at__date__lte=end)
        .values("paciente__complete_name", "paciente_id")
        .annotate(
            interacoes=Count("id"),
            entrada=Sum("input_tokens"),
            saida=Sum("output_tokens"),
            total=Sum("total_tokens"),
        )
        .order_by("-total")[:20]
    )