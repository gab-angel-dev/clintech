from django.contrib import admin
from .models import Arquivo, Embedding

admin.site.register([Arquivo, Embedding])
