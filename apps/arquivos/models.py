import os
from django.db import models
from pgvector.django import VectorField

class Arquivo(models.Model):
    class Categoria(models.TextChoices):
        INSTITUCIONAL = 'institucional', 'Institucional'
        PROCEDIMENTOS = 'procedimentos', 'Procedimentos'
        POLITICAS = 'politicas', 'Políticas Internas'

    class TipoMidia(models.TextChoices):
        PDF = 'pdf', 'PDF'
        DOCX = 'docx', 'DOCX'
        TXT = 'txt', 'TXT'

    categoria = models.CharField(max_length=100, choices=Categoria.choices)
    tipo_midia = models.CharField(max_length=50, choices=TipoMidia.choices)
    arquivo = models.FileField(upload_to='arquivos_rag/')
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.arquivo.name

    @property
    def nome_arquivo(self):
        nome = os.path.basename(self.arquivo.name).split('.')
        return nome[0]

    class Meta:
        db_table = 'arquivos'



class Embedding(models.Model):
    arquivo = models.ForeignKey(Arquivo, on_delete=models.CASCADE, related_name='embeddings')
    conteudo = models.TextField()
    categoria = models.CharField(max_length=100, null=True, blank=True)
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'embeddings'