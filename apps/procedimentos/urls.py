from django.urls import path
from . import views

app_name = 'procedimentos'

urlpatterns = [
    path('', views.procedimentos_view, name='procedimentos'),
    path('novo_procedimento/', views.novo_procedimento_view, name='novo_procedimento'),
    path('visualizar_procedimento/<int:pk>/', views.visualizar_procedimento_view, name='visualizar_procedimento')
]