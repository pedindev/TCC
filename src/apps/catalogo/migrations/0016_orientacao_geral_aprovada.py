from datetime import date

from django.db import migrations

SAC = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAR = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
PEDIDO = (
    "Solicito o boleto do imposto da mercadoria retida nos Correios. "
    "Código de rastreio: [COLOQUE SEU CÓDIGO]."
)
PEDIDO_DIFAL = (
    "Solicito o boleto do DIFAL da mercadoria retida nos Correios para encaminhar ao "
    "fornecedor. Código de rastreio: [COLOQUE SEU CÓDIGO]."
)
TEXTO = (
    "*SOLICITE O BOLETO*\n\n"
    "➡️ Acesse:\n" + SAC + "\n\n"
    "1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. "
    "Clique em *Próximo*.\n\n"
    "2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva:\n\n"
    "“" + PEDIDO + "”\n\n"
    "3️⃣ Clique em *Próximo*. Na resposta automática, escolha:\n"
    "*Não foi satisfatória. Desejo receber atendimento humano.*\n\n"
    "4️⃣ Na próxima tela, selecione:\n\n"
    "• Solicitação para você: *Sim*.\n"
    "• Solicitar como: *Cidadão*.\n"
    "• Temática: *Mercadorias em trânsito | Posto Fiscal*.\n"
    "• Categoria: *Cálculo do imposto*.\n"
    "• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.\n"
    "• Relacionada a processo: *Não*, se não houver processo relacionado.\n\n"
    "5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*\n\n"
    "Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, "
    "use esses dois códigos:\n" + ACOMPANHAR
)
TEXTOS = {
    "SAC-PEDIDO-GERAL": TEXTO,
    "SAC-PEDIDO-COM": TEXTO,
    "SAC-PEDIDO-SIM": TEXTO,
    "SAC-PEDIDO-DIF": TEXTO.replace(PEDIDO, PEDIDO_DIFAL),
}


def registrar_aprovacao_textual(apps, schema_editor):
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    for codigo, texto in TEXTOS.items():
        anterior = guias.get(codigo=codigo, versao=1)
        guias.get_or_create(
            codigo=codigo,
            versao=2,
            defaults={
                "titulo": anterior.titulo,
                "url": SAC,
                "texto": texto,
                "estado": "revisado",
                "verificado_em": date(2026, 11, 5),
                "observacoes": (
                    "Texto apresentado no chat e aprovado pelo autor em 05/11/2026, com "
                    "remoção exclusiva de ', se for seu próprio pedido'. Preservado o "
                    "restante da mensagem, inclusive links completos e acompanhamento. "
                    "GERAL/COM/SIM usam o texto geral; DIF usa a variante do pedido para "
                    "encaminhar ao fornecedor. Estado revisado registra a aprovação textual "
                    "do autor, não aprovação institucional, fiscal ou autorização de envio. "
                    "Fluxo descrito para cidadão em pedido próprio. SIMEI continua com "
                    "explicação fiscal provisória; regras de seleção SIAT e limites do "
                    "DIFAL permanecem nos requisitos. Não houve envio nem operação no SAC. "
                    "Orientações da migração 0015 preservadas como versões anteriores "
                    "para COM/SIM/DIF. Acompanhamento já incluído: usar guia complementar "
                    "apenas se necessário, evitando repetir mensagens."
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0015_orientacoes_curtas_por_categoria")]
    operations = [migrations.RunPython(registrar_aprovacao_textual)]
