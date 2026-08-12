from django.urls import path
from . import views


app_name = 'equipe'

urlpatterns = [
    path('', views.equipe_view, name='equipe'),
    path('admin_novo', views.admin_novo_view, name='admin_novo'),
    path('admin_editar/<int:pk>/', views.admin_editar_view, name='admin_editar'),
    path('admin_senha/<int:pk>/', views.admin_senha_view, name='admin_senha'),
    path('admin_deletar/<int:pk>/', views.admin_deletar_view, name='admin_deletar'),
    path('admin_toggle_ativo/<int:pk>/', views.admin_toggle_ativo_view, name='admin_toggle_ativo')
]