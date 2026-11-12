from datetime import date

from django.db import migrations

VERSOES = {
    "SAC-ABERTURA": 2,
    "SAC-PEDIDO-GERAL": 2,
    "SAC-PEDIDO-COM": 2,
    "SAC-PEDIDO-SIM": 2,
    "SAC-PEDIDO-DIF": 2,
    "SAC-PEDIDO-IRF": 3,
    "SAC-PEDIDO-NFA": 3,
}
PEDIDO_GERAL = (
    "Solicito o boleto do imposto da mercadoria retida nos Correios. "
    "Código de rastreio: [COLOQUE SEU CÓDIGO]."
)
PEDIDO_IRF = (
    "Minha mercadoria está retida por irregularidade fiscal. Quero saber qual é o "
    "problema e o que preciso fazer para resolver. Se houver imposto a pagar, "
    "solicito o boleto. Código de rastreio: [COLOQUE SEU CÓDIGO]."
)


def atualizar_orientacoes(apps, schema_editor):
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    geral = guias.get(codigo="SAC-PEDIDO-GERAL", versao=2)
    for codigo, versao in VERSOES.items():
        anterior = guias.get(codigo=codigo, versao=versao)
        texto = anterior.texto
        if codigo == "SAC-PEDIDO-IRF":
            texto = geral.texto.replace(
                "*SOLICITE O BOLETO*",
                "*SITUAÇÃO FISCAL IRREGULAR — SOLICITE INFORMAÇÕES E O BOLETO*",
            ).replace(PEDIDO_GERAL, PEDIDO_IRF)
        texto = texto.replace(", se não houver processo relacionado", "")
        texto = texto.replace(
            "Não se este pedido não estiver vinculado a um processo existente. "
            "Se houver vínculo, informe-o conforme as opções do portal.",
            "Não.",
        )
        guias.get_or_create(
            codigo=codigo,
            versao=versao + 1,
            defaults={
                "titulo": anterior.titulo,
                "url": anterior.url,
                "texto": texto,
                "estado": "revisado" if codigo == "SAC-PEDIDO-IRF" else anterior.estado,
                "verificado_em": date(2026, 11, 5),
                "observacoes": (
                    "Autor solicitou em 05/11/2026 retirar a condição 'se não houver processo "
                    "relacionado' de todas as mensagens atuais. Mantida a opção Não. "
                    "IRF: versão apresentada no chat aprovada textualmente, com essa única "
                    "remoção; inclui acompanhamento e segue o formato geral. Demais registros "
                    "mantêm seus estados de revisão. Revisão textual não é aprovação fiscal, "
                    "institucional ou autorização de envio; nenhum protocolo enviado. "
                    "Versões anteriores preservadas como histórico. Referência anterior: "
                    + anterior.observacoes
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0016_orientacao_geral_aprovada")]
    operations = [migrations.RunPython(atualizar_orientacoes)]
