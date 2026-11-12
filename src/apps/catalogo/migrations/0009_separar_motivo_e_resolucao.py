from django.db import migrations

TEXTOS = {
    "COM-01": (
        "Sua mercadoria está retida porque a fiscalização identificou características de "
        "compra para revenda. Isso pode acontecer pela quantidade de produtos ou pela "
        "frequência das compras, quando indicam que as mercadorias serão vendidas a outras "
        "pessoas. Nesse caso, há uma cobrança de imposto referente à mercadoria."
    ),
    "DIF-01": (
        "Sua mercadoria está retida porque há uma pendência no pagamento da parte do "
        "imposto dessa compra que cabe ao Piauí. Quando uma loja de outro estado vende "
        "para um consumidor no Piauí, o ICMS é dividido entre o estado de origem e o de "
        "destino. A diferença que cabe ao estado que recebe a mercadoria é chamada de "
        "DIFAL. Nas compras para uso pessoal, quando o comprador não é contribuinte de "
        "ICMS, quem deve pagar essa diferença é o fornecedor, ou seja, a loja que vendeu "
        "a mercadoria."
    ),
    "SIM-01": (
        "Sua mercadoria está retida porque há uma pendência de ICMS em uma compra que "
        "envolve um MEI, o Microempreendedor Individual. O ICMS é o imposto ligado à "
        "venda de mercadorias."
    ),
    "SNF-01": "Sua mercadoria está retida porque veio sem nota fiscal.",
    "IRF-01": (
        "Sua mercadoria está retida porque foi identificado um problema fiscal relacionado "
        "ao envio. Esse tipo de retenção pode ter motivos diferentes, e o aviso de "
        "irregularidade fiscal, sozinho, não informa qual é o problema no seu caso."
    ),
}


def separar_motivo_e_resolucao(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    for codigo, texto in TEXTOS.items():
        versao_anterior = 2 if codigo == "IRF-01" else 3
        anterior = orientacoes.get(codigo=codigo, versao=versao_anterior)
        orientacoes.get_or_create(
            codigo=codigo,
            versao=versao_anterior + 1,
            defaults={
                "categoria": anterior.categoria,
                "situacao": anterior.situacao,
                "texto": texto,
                "estado": "rascunho",
                "fontes": anterior.fontes,
                "dispositivo": anterior.dispositivo,
                "observacoes": (
                    "Separação solicitada pelo autor: primeira mensagem explica apenas o motivo "
                    "em linguagem simples; instruções, modelos e links ficam nos guias de "
                    "resolução. Usar somente após confirmar retenção e motivo no SIAT. "
                    "Comercialização: confirmar cobrança; quantidade ou frequência não geram "
                    "classificação automática nem limite numérico. DIFAL: responsabilidade do "
                    "fornecedor restrita ao consumidor final não contribuinte; não avaliar "
                    "enquadramento automaticamente. Sem nota: confirmar ausência de documento "
                    "exigível, não simples falha de consulta. SIMEI permanece provisória até "
                    "detalhamento do autor. Irregularidade não é resposta para resultado "
                    "desconhecido. Bases e limites em REQUISITOS.md e ORIENTACAO_PORTAL.md. "
                    "Versões anteriores preservadas; conteúdo ainda não aprovado para envio."
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0008_explicacoes_linguagem_simples")]
    operations = [migrations.RunPython(separar_motivo_e_resolucao)]
