from celery import shared_task
from .models import Arquivo, Embedding
from openai import OpenAI
from pypdf import PdfReader
from docx import Document
from decouple import config
from langchain_text_splitters import RecursiveCharacterTextSplitter


client = OpenAI(api_key=config('OPENAI_API_KEY'))

def extrair_texto(arquivo: Arquivo) -> str :
    caminho = arquivo.arquivo.path

    if arquivo.tipo_midia == Arquivo.TipoMidia.TXT:
        with open(caminho, 'r', encoding='utf-8') as f:
            texto = f.read()

    elif arquivo.tipo_midia == Arquivo.TipoMidia.PDF:
        leitor = PdfReader(caminho)
        texto = ""

        for pagina in leitor.pages:
            texto += pagina.extract_text() or ""

        if not texto.strip():
            return
        
    else: 
        documento = Document(caminho)
        texto = "\n".join(paragrafo.text for paragrafo in documento.paragraphs)

    return texto


@shared_task
def gerar_embeddings_task(arquivo_id):
    arquivo = Arquivo.objects.get(id=arquivo_id)

    texto = extrair_texto(arquivo)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=250,
        separators=["\n\n", "\n", " "]
    )

    chunks = splitter.split_text(texto)
    print(chunks)

    for chunk in chunks:
        try:
            response = client.embeddings.create(
                model='text-embedding-3-small',
                input=chunk
            )

        except Exception as exc:
            print(f"Erro ao gerar embedding para arquivo {arquivo_id}: {exc}")
            continue


        Embedding.objects.create(
            arquivo=arquivo,
            conteudo=chunk,
            categoria=arquivo.categoria,
            embedding=response.data[0].embedding
        )
       

        






# celery -A core worker --loglevel=info