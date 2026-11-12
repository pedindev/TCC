from django.db import migrations

SAC = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAR = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
PEDIDO_GUIA = (
    "Abra um pedido de atendimento no site da SEFAZ e peça o boleto do imposto. "
    "Informe o código de rastreio da encomenda, o mesmo que você usa para acompanhar "
    "a entrega. É por ele que a equipe vai localizar a mercadoria.\n\n"
    "Você pode escrever: Quero solicitar o boleto do imposto da minha encomenda "
    "que está retida nos Correios. Meu código de rastreio é: [CÓDIGO DE RASTREIO].\n\n"
    "Se o imposto já foi pago, explique isso no pedido para a equipe conferir."
)
TEXTOS = {
    "COM-01": (
        "Sua mercadoria está retida porque foi identificada como produto destinado à venda. "
        "A SEFAZ precisa verificar a situação do imposto dessa compra para dar andamento "
        "ao atendimento.\n\n" + PEDIDO_GUIA
    ),
    "DIF-01": (
        "Sua encomenda está retida por uma pendência no imposto de uma compra vinda de "
        "outro estado. Esse imposto é chamado de DIFAL: é a diferença entre os impostos "
        "dos estados envolvidos na compra. A equipe da SEFAZ precisa conferir essa "
        "pendência.\n\n" + PEDIDO_GUIA
    ),
    "SIM-01": (
        "Sua encomenda está retida por uma questão de imposto em uma compra que envolve "
        "um MEI, o Microempreendedor Individual. O imposto em questão é o ICMS, que está "
        "ligado à venda de mercadorias. A equipe da SEFAZ precisa analisar o caso e "
        "informar o que falta resolver.\n\n" + PEDIDO_GUIA
    ),
    "SNF-01": (
        "Sua encomenda está retida porque falta a nota fiscal que deveria acompanhar "
        "a mercadoria. Para pedir a análise da SEFAZ, você tem dois caminhos:\n\n"
        "Se a nota já foi emitida até a data da postagem nos Correios, peça uma cópia "
        "ao vendedor e anexe no pedido de atendimento. Informe também o código de rastreio. "
        "A equipe vai conferir se essa nota pode ser aceita.\n\n"
        "Você pode escrever: Estou enviando a nota fiscal da minha encomenda para análise. "
        "Meu código de rastreio é: [CÓDIGO DE RASTREIO]. O que falta fazer para resolver "
        "a retenção?\n\n"
        "Se não conseguir apresentar essa nota, peça à SEFAZ uma nota fiscal avulsa. "
        "É uma nota emitida para essa mercadoria, após a análise do pedido. "
        "Anexe o comprovante de pagamento da compra e informe o nome completo, o CPF "
        "e o endereço de quem vai receber a encomenda. Inclua o código de rastreio "
        "e diga que autoriza a emissão da nota.\n\n"
        "Você pode escrever: Quero solicitar uma nota fiscal avulsa para minha encomenda "
        "retida nos Correios. Código de rastreio: [CÓDIGO DE RASTREIO]. "
        "Nome de quem vai receber: [NOME COMPLETO]. CPF: [CPF]. "
        "Endereço: [ENDEREÇO COMPLETO, INCLUINDO CEP]. Estou anexando o comprovante "
        "de pagamento da compra e autorizo a emissão da nota fiscal avulsa."
    ),
    "IRF-01": (
        "Sua encomenda está retida porque foi encontrado um problema fiscal ligado "
        "ao envio da mercadoria. Esse aviso, sozinho, não informa qual é o problema. "
        "A equipe da SEFAZ precisa verificar o caso e explicar o que deve ser feito.\n\n"
        "Abra um pedido de atendimento no site da SEFAZ, informe o código de rastreio "
        "e peça que expliquem o motivo da retenção. Você também pode pedir o boleto, "
        "se houver imposto a pagar.\n\n"
        "Você pode escrever: Minha encomenda está retida por irregularidade fiscal. "
        "Quero saber qual é o problema e o que preciso fazer para resolver. "
        "Se houver imposto a pagar, peço o envio do boleto. "
        "Meu código de rastreio é: [CÓDIGO DE RASTREIO]."
    ),
}
FINAL_COMUM = (
    "\n\nAbra seu pedido aqui: " + SAC + "\n\n"
    "Quando aparecer a resposta automática, clique em Não foi satisfatória. "
    "Desejo receber atendimento humano para continuar o pedido ao PF Correios. "
    "Depois de finalizar, guarde o protocolo e o código de acesso. "
    "Aguarde a resposta da equipe do posto e acompanhe aqui: " + ACOMPANHAR
)


def simplificar_explicacoes(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    for codigo, texto in TEXTOS.items():
        versao_anterior = 1 if codigo == "IRF-01" else 2
        anterior = orientacoes.get(codigo=codigo, versao=versao_anterior)
        orientacoes.get_or_create(
            codigo=codigo,
            versao=versao_anterior + 1,
            defaults={
                "categoria": anterior.categoria,
                "situacao": anterior.situacao,
                "texto": texto + FINAL_COMUM,
                "estado": "rascunho",
                "fontes": anterior.fontes,
                "dispositivo": anterior.dispositivo,
                "observacoes": (
                    "Reescrita em linguagem simples a pedido do autor em 01/11/2026. "
                    "Reúne motivo, próximo passo, exemplo de pedido e links; não é aprovação "
                    "jurídica ou operacional. Boleto é o termo simples para a guia oficial "
                    "solicitada à SEFAZ, sem determinar dívida ou responsável. "
                    "Campos entre colchetes devem ser preenchidos no portal pelo contribuinte. "
                    "Usar após confirmar o motivo atual no SIAT. Não prometer liberação. "
                    "SIMEI permanece provisória; critério de postagem e documentos da NFA-e "
                    "são procedimentos relatados, com confirmação específica pendente. "
                    "Fontes, limites e campos de encaminhamento em ORIENTACAO_PORTAL.md. "
                    "Versões anteriores preservadas; notas abaixo são contexto histórico: "
                    + anterior.observacoes
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0007_fluxo_sac_correios")]
    operations = [migrations.RunPython(simplificar_explicacoes)]
