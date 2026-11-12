from django.db import migrations

ENVIO = (
    "Entre em contato com o fornecedor e peça uma cópia da nota fiscal da mercadoria, "
    "que deve ter sido emitida até a data da postagem nos Correios. Depois, envie a nota "
    "por este WhatsApp para análise da equipe do posto fiscal."
)
TEXTO = "Sua mercadoria está retida porque veio sem nota fiscal. " + ENVIO
NOTA = (
    "O autor confirmou que o código de rastreio é a primeira informação recebida no "
    "atendimento. Não pedi-lo novamente ao orientar o envio da nota pelo WhatsApp. "
    "Permanece necessário informar o rastreio nas solicitações abertas pelo contribuinte "
    "no portal, que é um canal separado. Esta mudança não implementa armazenamento ou "
    "vínculo de atendimentos. Demais limites do procedimento permanecem válidos."
)


def remover_pedido_repetido(apps, schema_editor):
    for modelo, codigo, anterior_versao, texto in (
        ("Orientacao", "SNF-01", 7, TEXTO),
        ("GuiaPortal", "SAC-PEDIDO-NF", 3, ENVIO),
    ):
        registros = apps.get_model("catalogo", modelo).objects.using(schema_editor.connection.alias)
        anterior = registros.get(codigo=codigo, versao=anterior_versao)
        campos = (
            ("categoria", "situacao", "fontes", "dispositivo")
            if modelo == "Orientacao"
            else ("titulo", "url", "verificado_em")
        )
        registros.get_or_create(
            codigo=codigo,
            versao=anterior_versao + 1,
            defaults={
                **{campo: getattr(anterior, campo) for campo in campos},
                "texto": texto,
                "estado": "rascunho",
                "observacoes": NOTA
                + " Referência histórica da revisão anterior: "
                + anterior.observacoes,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0012_nota_fornecedor_data_postagem")]
    operations = [migrations.RunPython(remover_pedido_repetido)]
