from apps.atendimento.erros import FalhaOperacao
from apps.errors import IntegracaoIndisponivel
from apps.siat.recuperacao import ResultadoConsulta, consultar_com_recuperacao
from apps.siat.resultado import ler_resultado_real


def consultar(
    identificador,
    *,
    page=None,
    avisar=lambda texto: None,
    verificar_continuacao=lambda: None,
    leitor=ler_resultado_real,
):
    """Recuperação existente seguida de um leitor explicitamente definido."""
    if page is None:
        raise IntegracaoIndisponivel("Conecte o navegador de atendimento antes de consultar.")
    resultado = consultar_com_recuperacao(
        page,
        identificador,
        avisar,
        verificar_continuacao=verificar_continuacao,
    )
    verificar_continuacao()
    if resultado == ResultadoConsulta.CONFERIR_MANUALMENTE:
        raise FalhaOperacao(
            "inconclusivo",
            "A situação da encomenda não pôde ser confirmada após o novo login.",
            "Confira a consulta manualmente no SIAT. O resultado vazio não confirma liberação.",
        )
    return leitor(page, identificador)
