# apps/core/migrations/0001_trigger_updated_at.py

from django.db import migrations

CRIAR_FUNCAO = """
    CREATE OR REPLACE FUNCTION set_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""

REMOVER_FUNCAO = """
    DROP FUNCTION IF EXISTS set_updated_at() CASCADE;
"""

# Toda tabela que tem updated_at e pode ser gravada por fora do Django.
TABELAS_COM_UPDATED_AT = [
    "pacientes",
    "agendamentos",
    "doutores",
    # adicione aqui outras conforme forem precisando
]


def criar_triggers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(CRIAR_FUNCAO)
        for tabela in TABELAS_COM_UPDATED_AT:
            cursor.execute(f"""
                DROP TRIGGER IF EXISTS trg_{tabela}_updated_at ON {tabela};
                CREATE TRIGGER trg_{tabela}_updated_at
                BEFORE UPDATE ON {tabela}
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """)


def remover_triggers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for tabela in TABELAS_COM_UPDATED_AT:
            cursor.execute(f"DROP TRIGGER IF EXISTS trg_{tabela}_updated_at ON {tabela};")
        cursor.execute(REMOVER_FUNCAO)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("agenda", "0001_initial"),
        ("arquivos", "0001_initial"),
        ("chat", "0001_initial"),
        ("doutores", "0001_initial"),
        ("home", "0001_initial"),
        ("pacientes", "0003_alter_pacientes_created_at_and_more"),
        ("procedimentos", "0005_alter_procedimento_triagem"),
    ]

    operations = [
        migrations.RunPython(criar_triggers, reverse_code=remover_triggers),
    ]