"""Verificação de tela e aviso de login; rota de login observada no SIAT real."""

from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page


class TelaConsultaIndisponivel(RuntimeError):
    """A página não apresentou um formulário de consulta inequívoco."""


class LoginSiatNecessario(TelaConsultaIndisponivel):
    """Login manual necessário; não solicita nem preenche credenciais."""


def verificar_login_necessario(page: Page) -> None:
    """Detecta a rota observada, sem guardar a URL ou eventuais IDs de sessão."""
    url = urlsplit(page.url)
    if (
        url.hostname == "webas.sefaz.pi.gov.br"
        and url.path.split(";", 1)[0] == "/siatweb/faces/login.xhtml"
    ):
        raise LoginSiatNecessario(
            "O SIAT está na tela de login. Entre novamente no navegador e tente continuar. "
            "A automação foi interrompida."
        )


def aguardar_formulario_consulta(page: Page, *, timeout_ms: int = 5000) -> None:
    """Confere controles visíveis antes de alterar o filtro ou o rastreio.

    Uma tela inesperada não comprova sessão expirada. A mensagem específica
    de login só aparece na rota observada. Papéis dos controles ainda precisam
    de validação pelo Python; o acesso real foi feito pela extensão do navegador.
    """
    if not 0 < timeout_ms <= 30000:
        raise ValueError("O timeout por etapa deve estar entre 1 e 30000 ms.")
    verificar_login_necessario(page)
    try:
        page.get_by_role("combobox").wait_for(state="visible", timeout=timeout_ms)
        page.get_by_role("textbox").wait_for(state="visible", timeout=timeout_ms)
        page.get_by_role("button", name="Consultar", exact=True).wait_for(
            state="visible", timeout=timeout_ms
        )
    except PlaywrightError:
        verificar_login_necessario(page)
        raise TelaConsultaIndisponivel(
            "A tela de consulta do SIAT não está pronta ou seus campos estão ambíguos. "
            "Abra Consultar Notificação. Se o SIAT pedir login, entre novamente e tente continuar."
        ) from None
