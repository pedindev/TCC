from django.db import migrations

ENVIO = (
    "Entre em contato com o fornecedor e peça uma cópia da nota fiscal da mercadoria, "
    "que deve ter sido emitida até a data da postagem nos Correios. Depois, envie a nota "
    "por este WhatsApp, junto com o código de rastreio da encomenda, para análise "
    "da equipe do posto fiscal."
)
TEXTO = "Sua mercadoria está retida porque veio sem nota fiscal. " + ENVIO
NOTA = (
    "Correção do autor: incluir contato com o fornecedor, cópia da nota já emitida até "
    "a data da postagem nos Correios e envio pelo WhatsApp com rastreio. Não orientar "
    "emissão retroativa nem alterar data. O corte pela postagem é procedimento informado "
    "pelo autor, com fundamento específico pendente de confirmação; aceitação depende "
    "da análise fiscal. Sem solicitação de nota avulsa nesta mensagem. "
    "Nenhum arquivo recebido ou armazenado pelo MVP. Histórico preservado."
)


def completar_orientacao(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    anterior = orientacoes.get(codigo="SNF-01", versao=6)
    orientacoes.get_or_create(
        codigo="SNF-01",
        versao=7,
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
    anterior_guia = guias.get(codigo="SAC-PEDIDO-NF", versao=2)
    guias.get_or_create(
        codigo="SAC-PEDIDO-NF",
        versao=3,
        defaults={
            "titulo": anterior_guia.titulo,
            "url": "",
            "texto": ENVIO,
            "estado": "rascunho",
            "verificado_em": anterior_guia.verificado_em,
            "observacoes": NOTA,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0011_nota_fiscal_por_whatsapp")]
    operations = [migrations.RunPython(completar_orientacao)]
