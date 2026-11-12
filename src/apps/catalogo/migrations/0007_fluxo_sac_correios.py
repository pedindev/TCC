from datetime import date

from django.db import migrations

ABERTURA = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAMENTO = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
CTN = (
    "https://www2.camara.leg.br/legin/fed/lei/1960-1969/"
    "lei-5172-25-outubro-1966-358971-normaatualizada-pl.html"
)
RICMS = (
    "https://www.diario.pi.gov.br/doe/files/diarios/anexo/"
    "5714d565-bd46-4f50-950d-7fa74dbdc549/"
    "DIARIO-OFICIAL-DO-ESTADO-DO-PIAUI-PUBLICACAO-N-47.pdf"
)
ORIGEM = (
    "Relato do autor e três capturas fornecidas em 01/11/2026. "
    "verificado_em registra a conferência dessas referências, não aprovação institucional "
    "nem teste completo do portal. Evidências em ORIENTACAO_PORTAL.md. "
    "Somente orientação manual; nenhum protocolo criado, consultado ou armazenado pelo MVP. "
)
GUIAS = [
    {
        "codigo": "SAC-ABERTURA",
        "versao": 2,
        "titulo": "Abrir atendimento para mercadoria retida nos Correios",
        "url": ABERTURA,
        "texto": (
            "1. Acesse o Serviço de Atendimento ao Cidadão (SAC) no portal da SEFAZ-PI. "
            "Na etapa Solicitante, preencha seus dados: CPF, nome completo, e-mail, confirmação "
            "do e-mail e telefone. Confira os contatos e informe se possui WhatsApp. "
            "Escolha os avisos que deseja receber entre as opções disponíveis: e-mail, SMS "
            "e WhatsApp, se oferecido. Selecione Próximo.\n\n"
            "2. Em Solicitação, no campo O que você deseja? (descreva de forma detalhada), "
            "explique seu pedido e informe o código de rastreio da mercadoria retida. "
            "Use o modelo correspondente ao motivo da retenção, substituindo os campos "
            "entre colchetes. Quando houver documentos para apresentar, utilize Anexo e "
            "confira se foram adicionados antes de selecionar Próximo.\n\n"
            "3. Na etapa Resposta Automática, para encaminhar este pedido ao atendimento "
            "do PF Correios, selecione Não foi satisfatória. Desejo receber atendimento humano. "
            "A opção A resposta foi satisfatória registra e finaliza o atendimento automático; "
            "ela não é o caminho deste pedido de atendimento humano.\n\n"
            "4. Em Informações da Solicitação, se o pedido for para você, marque Sim em "
            "Esta solicitação é para você? e selecione Cidadão em Desejo solicitar como. "
            "Se estiver representando outra pessoa, informe essa condição corretamente. "
            "Selecione:\n"
            "Temática: Mercadorias em trânsito | Posto Fiscal.\n"
            "Categoria: Cálculo do imposto.\n"
            "Unidades Organizacionais: GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS.\n"
            "Em A solicitação é relacionada a um processo?, marque Não se este pedido não "
            "estiver vinculado a um processo existente. Se houver vínculo, informe-o "
            "conforme as opções do portal.\n\n"
            "5. Confira os dados, o pedido, os anexos e a unidade de destino e finalize "
            "a solicitação. Guarde o protocolo e o código de acesso apresentados ao concluir. "
            "Eles serão necessários para acompanhar o atendimento no portal."
        ),
        "observacoes": ORIGEM
        + (
            "Capturas comprovam Solicitação, Resposta Automática e Registro do SAC. "
            "Seleção dos avisos e geração dos códigos ao finalizar são relatadas pelo autor, "
            "sem captura dessas telas. Não se confirmou exclusividade da resposta automática "
            "para transportadoras privadas. Sim/Não dependem da situação real. "
            "Versão 1 preservada como histórico."
        ),
    },
    {
        "codigo": "SAC-ACOMPANHAMENTO",
        "versao": 2,
        "titulo": "Acompanhar atendimento e conferir dados de acesso",
        "url": ACOMPANHAMENTO,
        "texto": (
            "Acesse Acompanhe sua solicitação no portal da SEFAZ-PI. Preencha Protocolo "
            "e Código de acesso com os dados recebidos ao concluir o pedido e confirme "
            "no botão verde com o símbolo de confirmação.\n\n"
            "Aguarde o atendimento pela supervisão do posto fiscal e acompanhe a resposta "
            "pelo portal, inclusive eventuais pedidos de documentos ou informações. "
            "Você poderá receber avisos pelo canal escolhido, conforme as opções "
            "disponibilizadas pelo SAC. Consulte o atendimento mesmo que o aviso não chegue. "
            "Um aviso não significa, por si só, que a mercadoria foi liberada.\n\n"
            "Se não conseguir acessar, confira se o protocolo e o código de acesso foram "
            "informados nos campos corretos, exatamente como recebidos, sem espaços extras "
            "ao copiar. Se não souber o código, use Esqueci o código de acesso e siga as "
            "instruções do portal. Se os dados estiverem corretos e o erro continuar, guarde-os "
            "antes de fechar o navegador, reabra-o e tente novamente. Se persistir, procure "
            "os canais oficiais de atendimento da SEFAZ-PI. Não é necessário abrir outro "
            "protocolo apenas para tentar corrigir um erro de acesso."
        ),
        "observacoes": ORIGEM
        + (
            "Campos iniciais, botão verde e opção de recuperação observados anteriormente "
            "na página pública. Supervisão, avisos e recomendação de reabrir o navegador "
            "informados pelo autor. Resultado, complementação, entrega de avisos e recuperação "
            "não testados. Não prometer prazo ou solução ao reiniciar. Versão 1 histórica."
        ),
    },
    {
        "codigo": "SAC-PEDIDO-GERAL",
        "versao": 1,
        "titulo": "Pedido de guia: comercialização, e-commerce / DIFAL e SIMEI",
        "url": ABERTURA,
        "texto": (
            "No campo de descrição, peça o envio da guia do imposto e informe o código de "
            "rastreio completo. Para os casos gerais de comercialização, e-commerce / DIFAL "
            "e SIMEI, você pode escrever:\n\n"
            "Solicito o envio da guia de recolhimento do imposto referente à mercadoria "
            "retida nos Correios, código de rastreio [CÓDIGO DE RASTREIO].\n\n"
            "Substitua o campo entre colchetes pelo código da sua mercadoria. Se houver "
            "alguma particularidade, como pagamento já realizado, descreva-a no pedido "
            "para análise do atendimento."
        ),
        "observacoes": ORIGEM
        + (
            "Pedido geral definido pelo autor para três categorias; não determina incidência, "
            "valor, responsável ou obrigação de pagar. SIMEI continua com explicação provisória. "
            "Não usar o pedido de guia como solução universal de qualquer divergência."
        ),
    },
    {
        "codigo": "SAC-PEDIDO-IRF",
        "versao": 1,
        "titulo": "Pedido de esclarecimentos sobre irregularidade fiscal",
        "url": ABERTURA,
        "texto": (
            "Para conhecer a irregularidade fiscal e as providências necessárias, peça "
            "esclarecimentos pelo SAC e informe o código de rastreio. Você pode escrever:\n\n"
            "Solicito informações sobre a irregularidade fiscal relacionada à mercadoria "
            "retida nos Correios, código de rastreio [CÓDIGO DE RASTREIO], e orientações para "
            "regularização. Solicito também o envio da guia de recolhimento, caso haja "
            "imposto a recolher.\n\n"
            "Substitua o campo entre colchetes pelo código da sua mercadoria. Os detalhes "
            "serão analisados pelo atendimento responsável no SAC."
        ),
        "observacoes": ORIGEM
        + "CTN, art. 198: "
        + CTN
        + (
            " . Ampara sigilo fiscal, mas não estabelece vedação geral ao WhatsApp. "
            "Norma interna específica não localizada. Encaminhamento ao SAC é procedimento "
            "informado pelo autor; não atribuir irregularidade a uma pessoa por presunção."
        ),
    },
    {
        "codigo": "SAC-PEDIDO-NF",
        "versao": 1,
        "titulo": "Sem nota fiscal: apresentar nota já emitida",
        "url": ABERTURA,
        "texto": (
            "Se houver nota fiscal da mercadoria já emitida até a data da postagem nos "
            "Correios, apresente-a em Anexo para análise da SEFAZ. Confira a data real do "
            "documento; não solicite alteração ou emissão com data retroativa. No campo "
            "de descrição, você pode escrever:\n\n"
            "Solicito a análise da nota fiscal anexada, referente à mercadoria retida "
            "nos Correios, código de rastreio [CÓDIGO DE RASTREIO], e orientações para "
            "regularização.\n\n"
            "Substitua o campo entre colchetes pelo código da sua mercadoria e confira "
            "o anexo. A apresentação da nota depende de análise e não garante a liberação. "
            "Se não for possível apresentar essa nota, utilize a orientação para solicitar "
            "nota fiscal avulsa."
        ),
        "observacoes": ORIGEM
        + "RICMS-PI, Anexo VI, art. 83, I, publicação original: "
        + RICMS
        + (
            " . Emissão antes da saída; não equivale a validar qualquer nota do mesmo dia "
            "da postagem. Corte de data da postagem é procedimento relatado pelo autor, "
            "cujo fundamento específico e aceitação pelo posto estão pendentes. Conferir "
            "legislação aplicável ao emitente e alterações vigentes. Não automatizar aceitação."
        ),
    },
    {
        "codigo": "SAC-PEDIDO-NFA",
        "versao": 1,
        "titulo": "Sem nota fiscal: solicitar nota fiscal avulsa",
        "url": ABERTURA,
        "texto": (
            "Se não for possível apresentar a nota já emitida no período indicado, solicite "
            "a nota fiscal avulsa pelo SAC. Anexe o comprovante de pagamento da mercadoria. "
            "Na descrição, informe o nome completo, o CPF e o endereço completo do "
            "destinatário, o código de rastreio e sua autorização para emissão. "
            "Você pode escrever:\n\n"
            "Solicito a emissão de nota fiscal avulsa para regularização da mercadoria "
            "retida nos Correios, código de rastreio [CÓDIGO DE RASTREIO]. "
            "Destinatário: [NOME COMPLETO], CPF [CPF], endereço [ENDEREÇO COMPLETO, "
            "INCLUINDO CEP]. Anexo o comprovante de pagamento da mercadoria. "
            "Autorizo a emissão da nota fiscal avulsa referente a essa mercadoria, "
            "conforme análise da SEFAZ.\n\n"
            "Preencha os campos entre colchetes diretamente no portal e confira se o "
            "comprovante foi anexado. O comprovante é o do pagamento da compra. "
            "A SEFAZ analisará o pedido e poderá solicitar informações complementares."
        ),
        "observacoes": ORIGEM
        + "RICMS-PI, Anexo VI, arts. 89 e 90, V, publicação original: "
        + RICMS
        + (
            " . Hipótese de NFA-e em ação fiscal localizada; vigência consolidada pendente. "
            "Comprovante, dados do destinatário e autorização são instruções operacionais "
            "do autor, não lista de requisitos comprovada nesses artigos. Só usar autorização "
            "quando o solicitante puder concedê-la. Dados e anexo permanecem no portal; "
            "o MVP guarda apenas o modelo com campos vazios."
        ),
    },
]


def registrar_fluxo_sac(apps, schema_editor):
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    for dados in GUIAS:
        guias.get_or_create(
            codigo=dados["codigo"],
            versao=dados["versao"],
            defaults={**dados, "verificado_em": date(2026, 11, 1), "estado": "rascunho"},
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0006_irregularidades_fiscais")]
    operations = [migrations.RunPython(registrar_fluxo_sac)]
