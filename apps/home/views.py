from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from weasyprint import HTML

from apps.accounts.decorators import htmx_login_required

from . import services
from .charts import grafico_barras, grafico_linha, grafico_pizza
from .utils import resolver_periodo
from .exchange import get_usd_brl_rate

# ========= MÉTRICAS ========================================================================================================

@login_required
def dashboard_metricas(request):
    return render(request, "home/metricas.html")


@htmx_login_required
def metricas_summary(request):
    start, end = resolver_periodo(request)
    dados = services.get_summary(start, end)
    return render(request, "home/partials/_summary_cards.html", {**dados, "start": start, "end": end})


@htmx_login_required
def metricas_appointments_by_month(request):
    return JsonResponse(services.get_appointments_by_month(), safe=False)


@htmx_login_required
def metricas_messages_by_day(request):
    start, end = resolver_periodo(request)
    return JsonResponse(services.get_messages_by_day(start, end), safe=False)


@htmx_login_required
def metricas_procedures_distribution(request):
    start, end = resolver_periodo(request)
    return JsonResponse(services.get_procedures_distribution(start, end), safe=False)


@htmx_login_required
def metricas_doctors_ranking(request):
    start, end = resolver_periodo(request)
    doutores = services.get_doctors_ranking(start, end)
    maior = max((d.total_agendamentos for d in doutores), default=0)
    return render(request, "home/partials/_doctors_ranking.html", {"doutores": doutores, "maior": maior})


@login_required
def metricas_report_pdf(request):
    start, end = resolver_periodo(request)

    summary = services.get_summary(start, end)
    agendamentos_mes = services.get_appointments_by_month()
    mensagens_dia = services.get_messages_by_day(start, end)
    procedimentos = services.get_procedures_distribution(start, end)
    doutores = services.get_doctors_ranking(start, end)
    agendamentos_lista = services.get_appointments_list(start, end)

    grafico_mes_b64 = grafico_barras(
        [d["mes"] for d in agendamentos_mes],
        [d["total"] for d in agendamentos_mes],
        "Agendamentos por mês",
    )
    grafico_msg_b64 = grafico_linha(
        [d["dia"] for d in mensagens_dia],
        {"Usuário": [d["usuario"] for d in mensagens_dia], "IA": [d["ia"] for d in mensagens_dia]},
        "Mensagens por dia",
    )
    grafico_proc_b64 = grafico_pizza(
        [p["procedimento"] for p in procedimentos],
        [p["total"] for p in procedimentos],
        "Distribuição de procedimentos",
    )

    html_string = render_to_string("home/relatorio_pdf.html", {
        "summary": summary,
        "start": start,
        "end": end,
        "grafico_mes": grafico_mes_b64,
        "grafico_msg": grafico_msg_b64,
        "grafico_proc": grafico_proc_b64,
        "doutores": doutores,
        "agendamentos": agendamentos_lista,
    })

    pdf_bytes = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="relatorio_{start}_{end}.pdf"'
    return response

# ========= CUSTOS ========================================================================================================

@login_required
def dashboard_custos(request):
    return render(request, "home/custos.html")


@login_required
def dashboard_custos(request):
    return render(request, "home/custos.html")


@htmx_login_required
def custos_summary(request):
    start, end = resolver_periodo(request)
    taxa = get_usd_brl_rate()
    dados = services.get_costs_summary(start, end, taxa)
    return render(request, "home/partials/_costs_summary_cards.html", dados)


@htmx_login_required
def custos_tokens_by_day(request):
    start, end = resolver_periodo(request)
    return JsonResponse(services.get_tokens_by_day(start, end), safe=False)


@htmx_login_required
def custos_cost_by_day(request):
    start, end = resolver_periodo(request)
    return JsonResponse(services.get_cost_by_day(start, end), safe=False)


@htmx_login_required
def custos_by_model(request):
    start, end = resolver_periodo(request)
    return JsonResponse(services.get_costs_by_model(start, end), safe=False)


@htmx_login_required
def custos_by_user(request):
    start, end = resolver_periodo(request)
    dados = services.get_costs_by_user(start, end)
    return render(request, "home/partials/_costs_by_user.html", {"usuarios": dados})