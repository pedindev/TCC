from datetime import date

from django.db import migrations

ABERTURA = (
    "https://portal.sefaz.pi.gov.br/servicos-institucional+"
    "servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337"
)
ACOMPANHAMENTO = "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
EXPLICACOES = {
    "COM-01": (
        "A retenção na categoria comercialização está relacionada a mercadorias identificadas "
        "como destinadas à venda. Nesses casos, a fiscalização verifica a regularidade fiscal "
        "da operação e as obrigações de ICMS aplicáveis."
    ),
    "SNF-01": (
        "A retenção por ausência de nota fiscal indica uma pendência na documentação exigida "
        "para acompanhar a mercadoria."
    ),
    "DIF-01": (
        "A retenção por DIFAL está relacionada a uma pendência no recolhimento do diferencial "
        "de alíquotas do ICMS, aplicável a determinadas operações entre estados destinadas a "
        "consumidor final."
    ),
    "SIM-01": (
        "A retenção na categoria SIMEI está relacionada a uma pendência de ICMS em operação "
        "envolvendo Microempreendedor Individual (MEI)."
    ),
}
GUIAS = [
    {
        "codigo": "SAC-ABERTURA",
        "titulo": "Abrir protocolo de atendimento",
        "url": ABERTURA,
        "texto": (
            "Para solicitar atendimento sobre a retenção, acesse o Serviço de Atendimento ao "
            "Cidadão (SAC) no portal da SEFAZ-PI. Na etapa Solicitante, preencha CPF, nome "
            "completo, e-mail, confirmação do e-mail e telefone; informe se possui WhatsApp. "
            "Selecione Próximo e siga as instruções apresentadas pelo portal para concluir a "
            "solicitação. Guarde o protocolo e o código de acesso para o acompanhamento."
        ),
        "observacoes": (
            "Página pública observada no navegador em 01/11/2026, sem preencher ou enviar dados. "
            "Etapas visíveis: Solicitante, Solicitação, Registro do SAC e Finalizado. "
            "Somente campos da primeira etapa verificados. Campos, assuntos, anexos e confirmação "
            "das etapas seguintes ainda precisam ser mapeados. Não se observou como são "
            "fornecidos o protocolo e o código. O tutorial completo está pendente. "
            "Orientação manual comum às quatro categorias; não automatizar o portal."
        ),
    },
    {
        "codigo": "SAC-ACOMPANHAMENTO",
        "titulo": "Acompanhar solicitação",
        "url": ACOMPANHAMENTO,
        "texto": (
            "Para acompanhar sua solicitação, acesse a página de Acompanhamento de Protocolo SAC "
            "da SEFAZ-PI. Informe o protocolo e o código de acesso nos campos correspondentes e "
            "confirme no botão verde com o símbolo de confirmação. Se não souber o código, "
            "utilize a opção Esqueci o código de acesso e siga as instruções do portal."
        ),
        "observacoes": (
            "Formulário e botão verde observados no navegador em 01/11/2026. A acessibilidade "
            "nomeia o botão como Publicar; visualmente ele exibe um símbolo de confirmação. "
            "Nenhuma consulta enviada. Não foram observados resultado de protocolo, respostas, "
            "complementações nem etapas de recuperação do código. Não coletar código ou protocolo "
            "no MVP, nem automatizar consulta ou acompanhamento."
        ),
    },
]


def registrar_escopo_manual(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    guias = apps.get_model("catalogo", "GuiaPortal").objects.using(schema_editor.connection.alias)
    for codigo, texto in EXPLICACOES.items():
        anterior = orientacoes.get(codigo=codigo, versao=1)
        orientacoes.get_or_create(
            codigo=codigo,
            versao=2,
            defaults={
                "categoria": anterior.categoria,
                "situacao": anterior.situacao,
                "texto": texto,
                "estado": "rascunho",
                "fontes": anterior.fontes,
                "dispositivo": anterior.dispositivo,
                "observacoes": (
                    "Escopo corrigido pelo autor em 01/11/2026: somente explicação geral da "
                    "retenção. Encaminhamento pelos guias SAC-ABERTURA e SAC-ACOMPANHAMENTO. "
                    "Não orientar cálculo, responsabilidade tributária, pagamento ou emissão "
                    "de documento fiscal. Revisão da explicação ainda pendente. "
                    + ("SIMEI provisória até explicação do autor. " if codigo == "SIM-01" else "")
                    + "Versão 1 preservada como histórico, não utilizar como texto atual."
                ),
            },
        )
    for dados in GUIAS:
        guias.get_or_create(
            codigo=dados["codigo"],
            versao=1,
            defaults={**dados, "verificado_em": date(2026, 11, 1), "estado": "rascunho"},
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0003_guiaportal")]
    operations = [migrations.RunPython(registrar_escopo_manual)]
