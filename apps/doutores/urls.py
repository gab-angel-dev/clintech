from django.urls import path
from . import views


app_name = 'doutores'

urlpatterns = [
    path('', views.doutores_view, name='doutores'),
    path('novo_doutor/', views.novo_doutor_view, name='novo_doutor'),
    path('visualizar_doutor/<int:pk>/', views.visualizar_doutor_view, name='visualizar_doutor'),
    path('toggle_ativo/<int:pk>/', views.toggle_ativo_view, name='toggle_ativo')
]