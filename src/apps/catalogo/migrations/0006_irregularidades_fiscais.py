from django.db import migrations


def cadastrar_irregularidades(apps, schema_editor):
    orientacoes = apps.get_model("catalogo", "Orientacao").objects.using(
        schema_editor.connection.alias
    )
    orientacoes.get_or_create(
        codigo="IRF-01",
        versao=1,
        defaults={
            "categoria": "irregularidades_fiscais",
            "situacao": "Retenção registrada na categoria irregularidades fiscais",
            "texto": (
                "A retenção por irregularidades fiscais indica uma pendência na situação fiscal "
                "relacionada à operação com a mercadoria. A identificação da pendência e a análise "
                "para sua regularização são realizadas pela SEFAZ."
            ),
            "estado": "rascunho",
            "fontes": [
                "Categoria informada pelo autor em 01/11/2026; fundamento específico pendente."
            ],
            "dispositivo": "",
            "observacoes": (
                "Quinta categoria definida pelo autor em 01/11/2026. Explicação geral provisória, "
                "sem atribuir pendência ao remetente ou destinatário, nem presumir dívida, "
                "irregularidade cadastral ou obrigação não cumprida. Código e descrição reais "
                "do SIAT ainda precisam ser mapeados; não usar como categoria genérica para "
                "resultados desconhecidos. Encaminhamento manual pelos guias SAC-ABERTURA e "
                "SAC-ACOMPANHAMENTO, comuns a todas as categorias. Não calcula impostos, "
                "determina pagamento ou automatiza o portal. A fonte registrada é a decisão "
                "de escopo do autor, não uma validação jurídica."
            ),
        },
    )


class Migration(migrations.Migration):
    dependencies = [("catalogo", "0005_alter_orientacao_categoria")]
    operations = [migrations.RunPython(cadastrar_irregularidades)]
