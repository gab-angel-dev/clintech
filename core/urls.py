from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('home/', include('apps.home.urls', namespace='home')),
    path('pacientes/', include('apps.pacientes.urls', namespace='pacientes')),
    path('chat/', include('apps.chat.urls', namespace='chat')),
    path('doutores/', include('apps.doutores.urls', namespace='doutores')),
    path('procedimentos/', include('apps.procedimentos.urls', namespace='procedimentos')),
    path('agenda/', include('apps.agenda.urls', namespace='agenda')),
    path('arquivos/', include('apps.arquivos.urls', namespace='arquivos')),
    path('equipe/', include('apps.equipe.urls', namespace='equipe'))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)