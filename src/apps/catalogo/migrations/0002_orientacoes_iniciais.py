from django.db import migrations

LC87 = (
    "https://www2.camara.leg.br/legin/fed/leicom/1996/"
    "leicomplementar-87-13-setembro-1996-370965-normaatualizada-pl.html"
)
LC123 = (
    "https://www2.camara.leg.br/legin/fed/leicom/2006/"
    "leicomplementar-123-14-dezembro-2006-548099-normaatualizada-pl.html"
)
RICMS = (
    "https://www.diario.pi.gov.br/doe/files/diarios/anexo/"
    "5714d565-bd46-4f50-950d-7fa74dbdc549/"
    "DIARIO-OFICIAL-DO-ESTADO-DO-PIAUI-PUBLICACAO-N-47.pdf"
)
LIMITE = (
    "Rascunho baseado no levantamento de 01/11/2026. Conferir redação estadual vigente, "
    "aplicação aos Correios e procedimento do posto antes do uso real. "
    "A categoria e a retenção atual devem ser confirmadas no SIAT. "
)
ORIENTACOES = [
    {
        "codigo": "COM-01",
        "categoria": "comercializacao",
        "situacao": "Retenção registrada na categoria comercialização",
        "texto": (
            "A retenção na categoria comercialização está relacionada a mercadorias identificadas "
            "como destinadas à venda. Nesses casos, a fiscalização verifica a regularidade fiscal "
            "da operação e as obrigações de ICMS aplicáveis. Para saber como proceder, solicite "
            "ao atendimento fiscal a orientação correspondente à situação da sua encomenda."
        ),
        "fontes": [LC87, RICMS],
        "dispositivo": "LC 87/1996, art. 4º; RICMS-PI, Anexo VII, art. 81, c (texto original).",
        "observacoes": LIMITE + "Explicação geral, sem presumir dívida ou falta de inscrição.",
    },
    {
        "codigo": "SNF-01",
        "categoria": "sem_nota_fiscal",
        "situacao": "Ausência confirmada de nota fiscal exigível",
        "texto": (
            "A retenção por ausência de nota fiscal indica uma pendência na documentação exigida "
            "para acompanhar a mercadoria. Verifique com o remetente se a nota fiscal foi emitida "
            "e informe essa situação ao atendimento fiscal para receber a orientação aplicável."
        ),
        "fontes": [RICMS],
        "dispositivo": "RICMS-PI, art. 164, § 1º, I, a (texto original).",
        "observacoes": LIMITE
        + (
            "Conferir dispensa e documentação aplicável. Não usar para documento apenas não "
            "localizado ou inválido. Não promete que apresentar nota resolve a retenção."
        ),
    },
    {
        "codigo": "DIF-01",
        "categoria": "difal",
        "situacao": "Pendência registrada de recolhimento do DIFAL",
        "texto": (
            "A retenção por DIFAL está relacionada a uma pendência no recolhimento do diferencial "
            "de alíquotas do ICMS, aplicável a determinadas operações entre estados destinadas a "
            "consumidor final. Verifique com o remetente se houve recolhimento referente à "
            "operação e solicite ao atendimento fiscal a conferência da pendência "
            "e a orientação sobre como proceder."
        ),
        "fontes": [LC87, RICMS],
        "dispositivo": (
            "LC 87/1996, art. 4º, § 2º; RICMS-PI, Anexo VII, art. 81, d (texto original)."
        ),
        "observacoes": LIMITE
        + (
            "Não selecionar apenas por compra online. Conferir responsável e pagamento; "
            "não atribuir dívida ao comprador nem orientar pagamento repetido."
        ),
    },
    {
        "codigo": "SIM-01",
        "categoria": "simei",
        "situacao": "Pendência de ICMS registrada na categoria SIMEI",
        "texto": (
            "A retenção na categoria SIMEI está relacionada a uma pendência de ICMS em operação "
            "envolvendo Microempreendedor Individual (MEI). Solicite ao atendimento fiscal a "
            "identificação da pendência e a orientação correspondente à sua encomenda."
        ),
        "fontes": [LC123, RICMS],
        "dispositivo": (
            "LC 123/2006, arts. 13, § 1º, XIII, e 18-A; "
            "RICMS-PI, Anexo VII, art. 81, b (texto original)."
        ),
        "observacoes": LIMITE
        + (
            "Provisória: aguarda explicação do autor prevista para 03/11/2026. Não presumir "
            "atraso de DAS, papel do MEI ou modalidade de cobrança."
        ),
    },
]


def cadastrar_orientacoes(apps, schema_editor):
    orientacao = apps.get_model("catalogo", "Orientacao")
    for dados in ORIENTACOES:
        orientacao.objects.using(schema_editor.connection.alias).get_or_create(
            codigo=dados["codigo"],
            versao=1,
            defaults={**dados, "estado": "rascunho"},
        )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0001_initial")]
    # Sem reversão automática: não apagar mensagens que possam ter sido editadas.
    operations = [migrations.RunPython(cadastrar_orientacoes)]
