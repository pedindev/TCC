from datetime import date

from django.db import migrations

SAC = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAR = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
INICIO = (
    "\n\n➡️ ACESSE O LINK:\n" + SAC + "\n\n"
    "Preencha com seus dados. Confira seus contatos e escolha como deseja receber avisos: "
    "e-mail, SMS ou WhatsApp, se essa opção estiver disponível. Clique em Próximo.\n\n"
)
FINAL = (
    "\n\n➡️ Na tela de resposta automática, clique em:\n"
    "Não foi satisfatória. Desejo receber atendimento humano.\n\n"
    "Na tela seguinte, selecione:\n"
    "● ESTA SOLICITAÇÃO É PARA VOCÊ? Sim, se o pedido for para você.\n"
    "● DESEJO SOLICITAR COMO: Cidadão, no pedido para você.\n"
    "● TEMÁTICA: Mercadorias em trânsito | Posto Fiscal.\n"
    "● CATEGORIA: Cálculo do imposto.\n"
    "● UNIDADES ORGANIZACIONAIS: GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS.\n"
    "● A SOLICITAÇÃO É RELACIONADA A UM PROCESSO? Não, se não estiver ligada a um "
    "processo já existente.\n\n"
    "Confira as informações e finalize. Guarde o protocolo e o código de acesso. "
    "Aguarde o atendimento da supervisão do posto fiscal.\n\n"
    "➡️ ACOMPANHE A RESPOSTA:\n" + ACOMPANHAR + "\n"
    "Use o protocolo e o código de acesso. Você poderá receber um aviso pelo contato "
    "escolhido; acompanhe pelo portal mesmo que o aviso não chegue.\n\n"
    "Se não conseguir acessar, confira os códigos exatamente como recebeu, sem espaços "
    "extras. Se continuar dando erro, guarde os códigos, feche e reabra o navegador. "
    "Se perdeu o código de acesso, use Esqueci o código de acesso."
)
TEXTOS = {
    "SAC-PEDIDO-IRF": (
        "SOLICITE INFORMAÇÕES SOBRE A IRREGULARIDADE FISCAL E O BOLETO:"
        + INICIO
        + (
            "➡️ No espaço O QUE VOCÊ DESEJA?, informe o código de rastreio e peça que "
            "expliquem qual é a irregularidade e o que precisa fazer para resolver. "
            "Peça também o boleto, caso haja imposto a pagar. Você pode escrever:\n\n"
            "Minha mercadoria está retida por irregularidade fiscal. Quero saber qual é "
            "o problema e o que preciso fazer para resolver. Se houver imposto a pagar, "
            "solicito o envio do boleto. Código de rastreio: [CÓDIGO DE RASTREIO].\n\n"
            "Substitua o campo entre colchetes pelo código da sua encomenda."
        )
        + FINAL
    ),
    "SAC-PEDIDO-NFA": (
        "SOLICITE A NOTA FISCAL AVULSA:"
        + INICIO
        + (
            "➡️ No espaço O QUE VOCÊ DESEJA?, solicite a nota fiscal avulsa. Informe o "
            "código de rastreio, o nome completo, o CPF e o endereço completo de quem "
            "vai receber a mercadoria. Escreva também que autoriza a emissão da nota. "
            "Você pode usar este texto:\n\n"
            "Quero solicitar uma nota fiscal avulsa para minha mercadoria retida nos "
            "Correios. Código de rastreio: [CÓDIGO DE RASTREIO]. Nome de quem vai receber: "
            "[NOME COMPLETO]. CPF: [CPF]. Endereço: [ENDEREÇO COMPLETO, INCLUINDO CEP]. "
            "Estou anexando o comprovante de pagamento da mercadoria e autorizo a "
            "emissão da nota fiscal avulsa.\n\n"
            "Substitua os campos entre colchetes pelos dados corretos.\n\n"
            "➡️ Em ANEXO, envie o comprovante de pagamento da compra da mercadoria. "
            "Confira se o arquivo foi anexado antes de clicar em Próximo."
        )
        + FINAL
    ),
}


def atualizar_solicitacoes(apps, schema_editor):
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
                "estado": "rascunho",
                "verificado_em": date(2026, 11, 2),
                "observacoes": (
                    "Versões completas a partir da mensagem-base fornecida pelo autor em "
                    "02/11/2026. Compõem a etapa de resolução, separada da explicação da "
                    "retenção. Código de rastreio preenchido no SAC, sem pedi-lo novamente "
                    "no WhatsApp. Nota avulsa somente quando não for possível apresentar "
                    "a nota existente; esta última continua pelo WhatsApp (SNF-01). "
                    "Comprovante é da compra, não do imposto. Usar o nome completo da unidade "
                    "PF CORREIOS, sem depender da posição 2 na lista. Botão humano conforme "
                    "captura anterior. Não preenchido ou enviado formulário real. "
                    "Data indica conferência do texto fornecido, não nova inspeção do portal. "
                    "Fontes e limites jurídicos permanecem em ORIENTACAO_PORTAL.md. "
                    "Referência histórica: " + anterior.observacoes
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0013_nota_sem_repetir_rastreio")]
    operations = [migrations.RunPython(atualizar_solicitacoes)]
