from datetime import date

from django.db import migrations

SAC = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAR = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
TEXTO = (
    "*SOLICITE A NOTA FISCAL AVULSA*\n\n"
    "➡️ Acesse:\n" + SAC + "\n\n"
    "1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. "
    "Clique em *Próximo*.\n\n"
    "2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva e substitua os campos entre colchetes. "
    "*Nome, CPF e endereço devem ser os dados do destinatário:*\n\n"
    "“Solicito e autorizo a emissão de nota fiscal avulsa para minha mercadoria "
    "retida nos Correios.\n"
    "Código de rastreio: [COLOQUE SEU CÓDIGO].\n"
    "Nome do destinatário: [NOME COMPLETO].\n"
    "CPF: [CPF].\n"
    "Endereço: [ENDEREÇO COMPLETO, INCLUINDO CEP].”\n\n"
    "📎 Em *Anexo*, envie o *comprovante de pagamento da compra da mercadoria*. "
    "Confira se o arquivo foi anexado.\n\n"
    "3️⃣ Clique em *Próximo*. Na resposta automática, escolha:\n"
    "*Não foi satisfatória. Desejo receber atendimento humano.*\n\n"
    "4️⃣ Na próxima tela, selecione:\n\n"
    "• Solicitação para você: *Sim*.\n"
    "• Solicitar como: *Cidadão*.\n"
    "• Temática: *Mercadorias em trânsito | Posto Fiscal*.\n"
    "• Categoria: *Cálculo do imposto*.\n"
    "• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.\n"
    "• Relacionada a processo: *Não*.\n\n"
    "5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*\n\n"
    "Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, "
    "use esses dois códigos:\n" + ACOMPANHAR
)


def salvar_nfa_aprovada(apps, schema_editor):
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    anterior = guias.get(codigo="SAC-PEDIDO-NFA", versao=4)
    guias.get_or_create(
        codigo="SAC-PEDIDO-NFA",
        versao=5,
        defaults={
            "titulo": anterior.titulo,
            "url": SAC,
            "texto": TEXTO,
            "estado": "revisado",
            "verificado_em": date(2026, 11, 5),
            "observacoes": (
                "Texto apresentado no chat e aprovado pelo autor em 05/11/2026. "
                "Substituído 'de quem vai receber' por 'do destinatário', deixando explícito "
                "que nome, CPF e endereço são os dados do destinatário. Restante da versão "
                "apresentada preservado, incluindo anexo, autorização, destino e links. "
                "Revisado significa aprovação textual do autor, não aprovação institucional "
                "ou autorização de envio. Não foi criado protocolo. Versão anterior histórica."
            ),
        },
    )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0017_retirar_condicao_processo")]
    operations = [migrations.RunPython(salvar_nfa_aprovada)]
