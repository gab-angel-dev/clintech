from django.urls import path

from . import views

app_name = "agenda"

urlpatterns = [
    path("", views.agenda_list, name="agenda"),
    path("eventos/", views.agenda_events, name="events"),
    path("disponibilidade/", views.agenda_availability, name="availability"),
    path("novo/", views.agenda_create, name="create"),
    path("pacientes/buscar/", views.agenda_patient_search, name="patient_search"),
    path("procedimento-convenio/", views.agenda_procedimento_convenio, name="procedimento_convenio"),
    path("<str:event_id>/detalhe/", views.agenda_event_detail, name="event_detail"),
    path("<str:event_id>/cancelar/", views.agenda_cancel, name="cancel"),
]