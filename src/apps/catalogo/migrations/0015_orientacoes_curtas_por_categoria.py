from datetime import date

from django.db import migrations

SAC = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAR = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
INICIO = (
    "\n\n➡️ Acesse:\n" + SAC + "\n\n"
    "1. Preencha seus dados e escolha os avisos disponíveis: e-mail, SMS ou WhatsApp. "
    "Clique em Próximo.\n\n"
    "2. Em *O QUE VOCÊ DESEJA?*, use o texto abaixo e substitua os campos entre colchetes:\n"
)
DESTINO = (
    "\n\n3. Clique em Próximo. Na resposta automática, escolha:\n"
    "*Não foi satisfatória. Desejo receber atendimento humano.*\n\n"
    "4. Preencha:\n"
    "• Pedido para você: *Sim* e *Cidadão*, se for seu próprio pedido.\n"
    "• Temática: *Mercadorias em trânsito | Posto Fiscal*.\n"
    "• Categoria: *Cálculo do imposto*.\n"
    "• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.\n"
    "• Relacionado a processo: *Não*, se não houver processo relacionado.\n\n"
    "5. Confira e finalize. *Guarde o protocolo e o código de acesso.*"
)
PEDIDO_BOLETO = (
    "Solicito o boleto do imposto da mercadoria retida nos Correios. "
    "Código de rastreio: [CÓDIGO DE RASTREIO]."
)
GUIAS = [
    (
        "SAC-PEDIDO-COM",
        1,
        "Solicitar boleto — Comercialização",
        "*SOLICITE O BOLETO — COMERCIALIZAÇÃO*" + INICIO + PEDIDO_BOLETO + DESTINO,
        SAC,
    ),
    (
        "SAC-PEDIDO-SIM",
        1,
        "Solicitar boleto — SIMEI",
        "*SOLICITE O BOLETO — SIMEI*" + INICIO + PEDIDO_BOLETO + DESTINO,
        SAC,
    ),
    (
        "SAC-PEDIDO-DIF",
        1,
        "Solicitar boleto — E-commerce / DIFAL",
        "*SOLICITE O BOLETO — E-COMMERCE / DIFAL*"
        + INICIO
        + "Solicito o boleto do DIFAL da mercadoria retida nos Correios para encaminhar "
        "ao fornecedor. Código de rastreio: [CÓDIGO DE RASTREIO]." + DESTINO,
        SAC,
    ),
    (
        "SAC-PEDIDO-IRF",
        3,
        "Solicitar esclarecimentos e boleto — Irregularidade fiscal",
        "*PEÇA INFORMAÇÕES SOBRE A IRREGULARIDADE E O BOLETO*"
        + INICIO
        + "Quero saber qual é a irregularidade fiscal da minha mercadoria e como resolver. "
        "Se houver imposto a pagar, solicito o boleto. "
        "Código de rastreio: [CÓDIGO DE RASTREIO]." + DESTINO,
        SAC,
    ),
    (
        "SAC-PEDIDO-NFA",
        3,
        "Solicitar nota fiscal avulsa",
        "*SOLICITE A NOTA FISCAL AVULSA*"
        + INICIO
        + "Solicito e autorizo a emissão de nota fiscal avulsa para minha mercadoria "
        "retida nos Correios.\n"
        "Rastreio: [CÓDIGO DE RASTREIO].\n"
        "Nome de quem vai receber: [NOME COMPLETO].\n"
        "CPF: [CPF].\n"
        "Endereço: [ENDEREÇO COMPLETO, INCLUINDO CEP].\n\n"
        "📎 Em *Anexo*, envie o comprovante de pagamento da mercadoria: "
        "é o comprovante da compra. Confira se o arquivo foi anexado." + DESTINO,
        SAC,
    ),
    (
        "SAC-ACOMPANHAMENTO",
        3,
        "Acompanhar solicitação — mensagem após finalizar o pedido",
        "*ACOMPANHE SUA SOLICITAÇÃO*\n\n"
        "➡️ " + ACOMPANHAR + "\n\n"
        "Digite o *protocolo* e o *código de acesso* recebidos ao finalizar o pedido. "
        "Confirme no botão verde.\n\n"
        "Aguarde o atendimento da supervisão do posto fiscal. Veja a resposta e eventuais "
        "pedidos de documentos pelo portal, mesmo que não chegue aviso por e-mail, SMS ou "
        "WhatsApp. O aviso não significa que a mercadoria já foi liberada.\n\n"
        "*Não conseguiu acessar?*\n"
        "• Confira o protocolo e o código de acesso, sem espaços extras.\n"
        "• Perdeu o código? Use *Esqueci o código de acesso*.\n"
        "• O erro continua? Guarde os códigos, feche e reabra o navegador. "
        "Se persistir, procure o atendimento oficial da SEFAZ. "
        "Não abra outro protocolo apenas por um erro de acesso.",
        ACOMPANHAR,
    ),
]


def cadastrar_mensagens_curtas(apps, schema_editor):
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    for codigo, versao, titulo, texto, url in GUIAS:
        guias.get_or_create(
            codigo=codigo,
            versao=versao,
            defaults={
                "titulo": titulo,
                "texto": texto,
                "url": url,
                "estado": "rascunho",
                "verificado_em": date(2026, 11, 2),
                "observacoes": (
                    "Formato curto solicitado pelo autor em 02/11/2026, com URLs literais "
                    "para copiar no WhatsApp. Enviar a orientação da categoria após a "
                    "explicação do motivo; acompanhamento é mensagem separada, após concluir "
                    "o pedido. Preserva etapas, dados, avisos, anexos, destino e recuperação, "
                    "sem repetir a mesma instrução antes e depois do exemplo. Não enviar "
                    "cinco solicitações à mesma pessoa. SAC-PEDIDO-GERAL v1 fica como "
                    "referência histórica, substituído pelos pedidos COM/SIM/DIF. "
                    "Rastreio já recebido no WhatsApp é informado pelo contribuinte no SAC. "
                    "SIMEI segue provisória; DIFAL para encaminhar ao fornecedor somente "
                    "na hipótese já explicada de consumidor final não contribuinte. "
                    "NFA somente quando não puder apresentar a nota existente; nota existente "
                    "continua pelo WhatsApp, sem repetir rastreio. Bases e limites em "
                    "ORIENTACAO_PORTAL.md. Data é da revisão textual; nenhum formulário "
                    "real foi preenchido, enviado ou consultado."
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0014_solicitacoes_irregularidade_nfa")]
    operations = [migrations.RunPython(cadastrar_mensagens_curtas)]
