"""Preenchimento e acionamento da pesquisa, sem interpretar a lista de resultados."""

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from apps.siat.estado import aguardar_formulario_consulta, verificar_login_necessario


class FalhaPesquisaSiat(RuntimeError):
    """Pesquisa interrompida; não representa ausência de notificação."""


class TempoPesquisaExcedido(FalhaPesquisaSiat):
    """A resposta nova não foi confirmada dentro do prazo da etapa."""


def pesquisar_rastreio(
    page: Page, codigo: str, *, timeout_ms: int = 5000, aguardar_atualizacao: bool = False
) -> None:
    """Reutiliza a tela aberta: seleciona Cód. Rastreio, substitui o campo e clica.

    O retorno indica somente que o clique terminou. Não confirma carregamento,
    resultado ou situação fiscal. Não retorna linhas que possam pertencer à
    pesquisa anterior. Não navega pelos menus nem repete cliques após erro.
    Com aguardar_atualizacao, exige a substituição AJAX do formulário observada
    no teste fictício no SIAT, antes de permitir a interpretação da mensagem.
    """
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("Informe o código de rastreio.")
    codigo = codigo.strip()
    if any(caractere.isspace() for caractere in codigo):
        raise ValueError("O código de rastreio não deve conter espaços ou quebras de linha.")

    aguardar_formulario_consulta(page, timeout_ms=timeout_ms)
    etapa = "seleção do tipo de pesquisa"
    formulario = None
    try:
        page.get_by_role("combobox").select_option(label="Cód. Rastreio", timeout=timeout_ms)
        etapa = "preenchimento do rastreio"
        page.get_by_role("textbox").fill(codigo, timeout=timeout_ms)
        if aguardar_atualizacao:
            formulario = page.locator('form[id="frmConsultar"]').element_handle(timeout=timeout_ms)
        etapa = "acionamento da consulta"
        page.get_by_role("button", name="Consultar", exact=True).click(timeout=timeout_ms)
        verificar_login_necessario(page)
        if aguardar_atualizacao:
            etapa = "atualização do formulário"
            page.wait_for_function(
                "formulario => !formulario.isConnected", arg=formulario, timeout=timeout_ms
            )
            aguardar_formulario_consulta(page, timeout_ms=timeout_ms)
    except PlaywrightTimeout:
        verificar_login_necessario(page)
        raise TempoPesquisaExcedido(
            "O SIAT demorou para confirmar a consulta. Confira o navegador e tente novamente."
        ) from None
    except PlaywrightError:
        verificar_login_necessario(page)
        raise FalhaPesquisaSiat(
            f"Pesquisa interrompida na etapa de {etapa}. "
            "Confira a tela antes de tentar novamente; nenhum resultado foi confirmado."
        ) from None
    finally:
        if formulario is not None:
            try:
                formulario.dispose()
            except PlaywrightError:
                # A navegação para login pode já ter destruído o contexto antigo.
                pass
