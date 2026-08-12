from django.urls import path
from . import views


app_name = 'arquivos'

urlpatterns = [
    # arquivos
    path('',                                views.arquivos_view,            name='arquivos'),
    path('arquivo_novo/',                   views.arquivo_novo_view,        name='arquivo_novo'),
    path('arquivo_deletar/<int:pk>/',       views.arquivo_deletar_view,     name='arquivo_deletar'),

    # embeddings
    path('embeddings/',                     views.embedding_view,      name='embeddings'),
    path('embedding_info/<int:pk>/',        views.embedding_info_view,      name='embedding_info'),
]