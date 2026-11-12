from django.db import migrations

SAC = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
TEXTOS = {
    "COM-01": (
        "Sua mercadoria está retida porque a fiscalização identificou características de "
        "compra para revenda. Isso pode acontecer pela quantidade de produtos ou pela "
        "habitualidade das compras, quando indicam que as mercadorias serão vendidas a outras "
        "pessoas. Nesse caso, há uma cobrança de imposto referente à mercadoria."
    ),
    "SNF-01": (
        "Sua mercadoria está retida porque veio sem nota fiscal. Envie a nota fiscal "
        "pelo portal de atendimento da SEFAZ: " + SAC + ". "
        "Ao preencher o pedido, use a opção Anexo para adicionar a nota e informe o "
        "código de rastreio da encomenda na descrição. Confira se o arquivo foi anexado "
        "antes de finalizar. A equipe do posto fiscal vai analisar o documento enviado."
    ),
}


def ajustar_mensagens(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    for codigo, texto in TEXTOS.items():
        anterior = orientacoes.get(codigo=codigo, versao=4)
        orientacoes.get_or_create(
            codigo=codigo,
            versao=5,
            defaults={
                "categoria": anterior.categoria,
                "situacao": anterior.situacao,
                "texto": texto,
                "estado": "rascunho",
                "fontes": anterior.fontes,
                "dispositivo": anterior.dispositivo,
                "observacoes": (
                    "Ajuste solicitado pelo autor: usar habitualidade na comercialização; "
                    "em sem nota fiscal, incluir já na primeira mensagem o envio da nota "
                    "pelo SAC, sem pedido de nota avulsa. Essa é uma exceção ao padrão de "
                    "separar motivo e resolução. Guias auxiliares preservados; não acrescentar "
                    "automaticamente o pedido de nota avulsa a esta mensagem. Confirmar motivo "
                    "no SIAT e cobrança antes de usar comercialização. Quantidade ou "
                    "habitualidade não determinam classificação automática. Em sem nota, "
                    "confirmar ausência do documento exigível; aceitação e data da nota "
                    "dependem da análise fiscal. Bases e limites em ORIENTACAO_PORTAL.md. "
                    "Histórico preservado; não representa aprovação para envio."
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0009_separar_motivo_e_resolucao")]
    operations = [migrations.RunPython(ajustar_mensagens)]
