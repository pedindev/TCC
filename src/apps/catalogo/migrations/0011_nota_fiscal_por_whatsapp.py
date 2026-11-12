from django.db import migrations, models

ENVIO = (
    "Envie a nota fiscal por este WhatsApp e informe o código de rastreio da encomenda, "
    "para que a equipe do posto fiscal possa localizar a mercadoria e analisar o documento."
)
TEXTO = "Sua mercadoria está retida porque veio sem nota fiscal. " + ENVIO
NOTA = (
    "Correção expressa do autor: nota fiscal já existente deve ser enviada pelo WhatsApp; "
    "o portal é destinado às solicitações. Esta orientação não pede nota fiscal avulsa "
    "nem envio da nota pelo SAC. Não foi informado número ou link de WhatsApp: o texto "
    "se refere à conversa de atendimento institucional. Sem automação de recepção, download "
    "ou armazenamento de documentos no MVP. Aceitação depende de análise fiscal. "
    "Versão anterior mantida apenas como histórico; conteúdo permanece em rascunho."
)


def corrigir_canal(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    anterior = orientacoes.get(codigo="SNF-01", versao=5)
    orientacoes.get_or_create(
        codigo="SNF-01",
        versao=6,
        defaults={
            "categoria": anterior.categoria,
            "situacao": anterior.situacao,
            "texto": TEXTO,
            "estado": "rascunho",
            "fontes": anterior.fontes,
            "dispositivo": anterior.dispositivo,
            "observacoes": NOTA,
        },
    )
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    guia_anterior = guias.get(codigo="SAC-PEDIDO-NF", versao=1)
    guias.get_or_create(
        codigo="SAC-PEDIDO-NF",
        versao=2,
        defaults={
            "titulo": "Enviar a nota fiscal pelo WhatsApp",
            "url": "",
            "texto": ENVIO,
            "estado": "rascunho",
            "verificado_em": guia_anterior.verificado_em,
            "observacoes": NOTA + " Código histórico preservado para versionamento.",
        },
    )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0010_habitualidade_e_envio_nota")]
    operations = [
        migrations.AlterField(
            model_name="guiaportal",
            name="url",
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.RunPython(corrigir_canal),
    ]
