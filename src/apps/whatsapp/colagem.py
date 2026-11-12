"""Colagem no campo escolhido pelo operador. Nenhuma ação de envio existe aqui."""

import re

from playwright.sync_api import Error as PlaywrightError

from apps.atendimento.erros import FalhaOperacao


def texto_do_editor(texto):
    # Editores contenteditable representam parágrafos vazios com blocos/BRs;
    # innerText pode acrescentar uma quebra visual. Não remove palavras ou parágrafos.
    return re.sub(r"\n{3,}", "\n\n", texto.replace("\r\n", "\n").replace("\u00a0", " ")).strip()


def colar_no_campo(page, seletor, texto):
    """Não seleciona conversa, não muda foco, não substitui rascunho e não usa Enter."""
    if not seletor:
        raise FalhaOperacao(
            "whatsapp_indisponivel",
            "O campo de mensagem do WhatsApp não foi confirmado.",
            "Mantenha a orientação no painel e confirme a configuração do navegador.",
        )
    try:
        campo = page.locator(seletor)
        pronto = campo.count() == 1 and campo.evaluate("""el =>
            document.visibilityState === 'visible' && document.hasFocus() &&
            document.activeElement === el && el.isContentEditable &&
            el.getClientRects().length > 0 && !el.innerText.trim()
        """)
        if not pronto:
            raise FalhaOperacao(
                "campo_sem_foco",
                "O texto não foi colado: o campo de mensagem não está pronto.",
                "Abra a conversa certa, deixe o campo vazio, clique nele e tente colar novamente.",
            )
        page.keyboard.insert_text(texto)
        if texto_do_editor(campo.inner_text()) != texto_do_editor(texto):
            raise FalhaOperacao(
                "colagem_incerta",
                "Não foi possível confirmar a colagem completa.",
                "Confira o campo no WhatsApp. Não repita a colagem sem verificar o conteúdo.",
            )
    except PlaywrightError:
        raise FalhaOperacao(
            "colagem_incerta",
            "A comunicação com o WhatsApp falhou durante a colagem.",
            "Confira o conteúdo no navegador antes de tentar qualquer nova ação.",
        ) from None
