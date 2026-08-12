from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('conversa/<str:phone_number>/', views.chat_conversa_view, name='conversa'),
    path('buscar_pacientes/', views.chat_buscar_pacientes_view, name='buscar_pacientes'),
    path('conversa/<str:phone_number>/enviar/', views.chat_enviar_mensagem_view, name='enviar_mensagem'),
    path('conversa/<str:phone_number>/toggle/', views.chat_toggle_atendimento_view, name='toggle_atendimento'),
    path('conversa/<str:phone_number>/novas/', views.chat_novas_mensagens_view, name='novas_mensagens'),
]