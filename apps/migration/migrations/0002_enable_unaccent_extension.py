# apps/core/migrations/0002_enable_unaccent_extension.py

from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):
    """
    Habilita a extensão unaccent no Postgres.

    ATENÇÃO — PRODUÇÃO (VPS/Docker):
    O usuário que o Django usa para conectar no banco (settings.DATABASES)
    provavelmente NÃO é superuser. `CREATE EXTENSION` exige privilégio
    especial, então essa migration só vai rodar sozinha se o usuário do
    Django tiver permissão de superuser/CREATE no banco.

    Se não tiver, rode manualmente ANTES do deploy, como superuser:

        docker exec -it <container_postgres> psql -U postgres -d <seu_banco> \\
            -c "CREATE EXTENSION IF NOT EXISTS unaccent;"

    E troque `operations` abaixo para usar SeparateDatabaseAndState, assim
    o Django só registra a migration como aplicada, sem tentar executar
    o CREATE EXTENSION de novo (evita erro de permissão no deploy):

        operations = [
            migrations.SeparateDatabaseAndState(
                state_operations=[UnaccentExtension()],
                database_operations=[],
            ),
        ]
    """

    dependencies = [
        ("migration", "0001_trigger_updated_at"),
    ]

    operations = [
        UnaccentExtension(),
    ]