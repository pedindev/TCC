"""Entrada na área de trabalho: Trânsito > Notificação Correios > Consultar.

Recebe a página SIAT já autenticada e controlada pelo Playwright. Não abre um
navegador nem faz login. Após entrar, verifica os controles da tela de consulta.
Esta preparação é independente da consulta de cada encomenda. Não chamar
automaticamente para cada rastreio; reutilizar a tela de consulta já aberta.
"""

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from apps.siat.estado import aguardar_formulario_consulta, verificar_login_necessario


class FalhaNavegacaoSiat(RuntimeError):
    """Interrompe o percurso sem expor conteúdo ou URL da página."""


def abrir_consulta_notificacao(page: Page, *, timeout_ms: int = 5000) -> None:
    """Abre os submenus por hover e clica somente em Consultar Notificação.

    Os textos vêm das capturas; o comportamento por hover é uma hipótese a
    validar na interface real. Cada ação tem espera limitada. Correspondências
    ausentes ou duplicadas interrompem o percurso, sem escolher a primeira.
    Após o clique, verifica o formulário e avisa caso o SIAT peça novo login.
    Executar somente quando for necessário entrar na área de consulta. A futura
    coordenação deve verificar a tela atual, em vez de repetir este percurso
    ou considerar a sessão pronta apenas porque já executou o clique uma vez.
    """
    if not 0 < timeout_ms <= 30000:
        raise ValueError("O timeout por etapa deve estar entre 1 e 30000 ms.")
    verificar_login_necessario(page)

    etapa = "Trânsito"
    try:
        page.get_by_text(etapa, exact=True).hover(timeout=timeout_ms)
        etapa = "Notificação Correios"
        page.get_by_text(etapa, exact=True).hover(timeout=timeout_ms)
        etapa = "Consultar Notificação"
        page.get_by_text(etapa, exact=True).click(timeout=timeout_ms)
    except PlaywrightError:
        verificar_login_necessario(page)
        raise FalhaNavegacaoSiat(
            f"Navegação interrompida na etapa '{etapa}'. "
            "Confira a sessão e o menu no navegador antes de tentar novamente."
        ) from None
    aguardar_formulario_consulta(page, timeout_ms=timeout_ms)
