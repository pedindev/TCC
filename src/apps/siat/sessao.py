"""Observação de sessão e espera pelo login manual; nunca lê credenciais."""

import re
from collections.abc import Callable
from enum import Enum
from time import monotonic
from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from apps.siat.estado import LoginSiatNecessario, TelaConsultaIndisponivel

SAIR = re.compile(r"^Sair(?:\s+Sair)?$")


class EstadoSessao(Enum):
    LOGIN = "login_necessario"
    INICIO = "inicio"
    CONSULTA = "consulta"
    DESCONHECIDA = "tela_nao_reconhecida"


def estado_sessao(page: Page) -> EstadoSessao:
    """Inspeciona somente rota e presença de controles, sem ler dados dos campos."""
    try:
        url = urlsplit(page.url)
        if url.hostname != "webas.sefaz.pi.gov.br":
            return EstadoSessao.DESCONHECIDA
        if url.path.split(";", 1)[0] == "/siatweb/faces/login.xhtml":
            return EstadoSessao.LOGIN
        if not page.get_by_role("link", name=SAIR).is_visible():
            return EstadoSessao.DESCONHECIDA
        if page.locator('form[id="frmConsultar"]').is_visible():
            return EstadoSessao.CONSULTA
        if (
            page.get_by_text(
                "Bem-vindo(a) a Central de Atendimento ao Contribuinte.", exact=False
            ).is_visible()
            and page.get_by_text("Trânsito", exact=True).is_visible()
        ):
            return EstadoSessao.INICIO
    except PlaywrightError:
        pass
    return EstadoSessao.DESCONHECIDA


def monitorar_sessao(
    page: Page,
    informar: Callable[[EstadoSessao], None],
    parar: Callable[[], bool],
    *,
    intervalo_ms: int = 500,
) -> None:
    """Monitor contínuo para o futuro worker que possui a Page, inclusive ocioso.

    Publica mudanças de estado. Não usar outra thread para acessar a mesma Page;
    durante uma consulta, o próprio fluxo faz as verificações de sessão.
    """
    if not 100 <= intervalo_ms <= 5000:
        raise ValueError("O intervalo deve estar entre 100 e 5000 ms.")
    anterior = None
    while not parar():
        atual = estado_sessao(page)
        if atual != anterior:
            informar(atual)
            anterior = atual
        if page.is_closed():
            return
        try:
            page.wait_for_timeout(intervalo_ms)
        except PlaywrightError:
            informar(EstadoSessao.DESCONHECIDA)
            return


def aguardar_login_manual(
    page: Page,
    avisar: Callable[[str], None],
    *,
    timeout_ms: int = 300000,
    verificar_continuacao: Callable[[], None] = lambda: None,
) -> None:
    if not 0 < timeout_ms <= 1800000:
        raise ValueError("O prazo de login deve estar entre 1 e 1800000 ms.")
    avisar("Faça login novamente no SIAT pelo navegador. A consulta será repetida após o login.")
    limite = monotonic() + timeout_ms / 1000
    while monotonic() < limite:
        verificar_continuacao()
        if estado_sessao(page) in (EstadoSessao.INICIO, EstadoSessao.CONSULTA):
            return
        if page.is_closed():
            raise TelaConsultaIndisponivel("O navegador do SIAT foi fechado.")
        try:
            page.wait_for_timeout(min(500, max(1, (limite - monotonic()) * 1000)))
        except PlaywrightError:
            raise TelaConsultaIndisponivel("Não foi possível acompanhar o login no SIAT.") from None
    raise LoginSiatNecessario(
        "O login no SIAT não foi confirmado no prazo. Inicie a consulta novamente."
    )


def sair_do_siat(page: Page, *, timeout_ms: int = 5000) -> None:
    """Aciona o link Sair observado, confirmando o retorno ao login."""
    try:
        page.get_by_role("link", name=SAIR).click(timeout=timeout_ms)
        page.wait_for_url(
            lambda url: (
                urlsplit(url).hostname == "webas.sefaz.pi.gov.br"
                and urlsplit(url).path.split(";", 1)[0] == "/siatweb/faces/login.xhtml"
            ),
            timeout=timeout_ms,
        )
    except PlaywrightError:
        raise TelaConsultaIndisponivel(
            "Não foi possível confirmar a saída do SIAT. Confira o navegador."
        ) from None
