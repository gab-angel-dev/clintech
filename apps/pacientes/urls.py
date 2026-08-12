from django.urls import path
from . import views


app_name = 'pacientes'

urlpatterns = [
    path('', views.pacientes_view, name='pacientes'),
    path('novo_paciente', views.novo_paciente_view, name='novo_paciente'),
    path('deletar_paciente/<str:phone_number>/', views.deletar_paciente_view, name='deletar_paciente'),
    path('visualizar_paciente/<str:phone_number>/', views.visualizar_paciente_view, name='visualizar_paciente'),
    path('listar_pacientes/', views.listar_pacientes_view, name='listar_pacientes'),
]