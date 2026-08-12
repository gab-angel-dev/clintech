from django.urls import path
from . import views


app_name = "home"

urlpatterns = [
    path("metricas/", views.dashboard_metricas, name="metricas"),
    path("custos/", views.dashboard_custos, name="custos"),
    path("metricas/summary/", views.metricas_summary, name="metricas_summary"),
    path("metricas/agendamentos-por-mes/", views.metricas_appointments_by_month, name="metricas_appointments_by_month"),
    path("metricas/mensagens-por-dia/", views.metricas_messages_by_day, name="metricas_messages_by_day"),
    path("metricas/distribuicao-procedimentos/", views.metricas_procedures_distribution, name="metricas_procedures_distribution"),
    path("metricas/ranking-doutores/", views.metricas_doctors_ranking, name="metricas_doctors_ranking"),
    path("metricas/relatorio/", views.metricas_report_pdf, name="metricas_report_pdf"),
    path("custos/summary/", views.custos_summary, name="custos_summary"),
    path("custos/tokens-por-dia/", views.custos_tokens_by_day, name="custos_tokens_by_day"),
    path("custos/custo-por-dia/", views.custos_cost_by_day, name="custos_cost_by_day"),
    path("custos/por-modelo/", views.custos_by_model, name="custos_by_model"),
    path("custos/por-usuario/", views.custos_by_user, name="custos_by_user"),
]