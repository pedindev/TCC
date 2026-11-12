from django.db import models


class Orientacao(models.Model):
    class Categoria(models.TextChoices):
        COMERCIALIZACAO = "comercializacao", "Comercialização"
        SIMEI = "simei", "SIMEI"
        SEM_NOTA_FISCAL = "sem_nota_fiscal", "Sem nota fiscal"
        DIFAL = "difal", "E-commerce / DIFAL"
        IRREGULARIDADES_FISCAIS = "irregularidades_fiscais", "Irregularidades fiscais"

    class Estado(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        REVISADO = "revisado", "Revisado"

    codigo = models.CharField(max_length=20)
    versao = models.PositiveIntegerField(default=1)
    categoria = models.CharField(max_length=30, choices=Categoria.choices)
    situacao = models.CharField(max_length=200)
    texto = models.TextField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.RASCUNHO)
    fontes = models.JSONField(default=list)
    dispositivo = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    revisado_por = models.CharField(max_length=150, blank=True)
    revisado_em = models.DateField(null=True, blank=True)
    vigencia_inicio = models.DateField(null=True, blank=True)
    vigencia_fim = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["codigo", "versao"]
        constraints = [
            models.UniqueConstraint(fields=["codigo", "versao"], name="orientacao_codigo_versao")
        ]

    def __str__(self):
        return f"{self.codigo} v{self.versao} — {self.get_categoria_display()}"


class GuiaPortal(models.Model):
    """Guias e modelos de pedido; nao armazena protocolos de contribuintes."""

    codigo = models.CharField(max_length=30)
    versao = models.PositiveIntegerField(default=1)
    titulo = models.CharField(max_length=150)
    url = models.URLField(max_length=500, blank=True)
    texto = models.TextField()
    observacoes = models.TextField(blank=True)
    verificado_em = models.DateField()
    estado = models.CharField(
        max_length=20, choices=Orientacao.Estado.choices, default=Orientacao.Estado.RASCUNHO
    )

    class Meta:
        ordering = ["codigo", "versao"]
        constraints = [
            models.UniqueConstraint(fields=["codigo", "versao"], name="guia_portal_codigo_versao")
        ]

    def __str__(self):
        return f"{self.codigo} v{self.versao} — {self.titulo}"
