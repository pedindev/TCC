import os
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from playwright.sync_api import sync_playwright

from apps.atendimento.erros import FalhaOperacao
from apps.whatsapp.colagem import colar_no_campo


class ColagemBrowserCheck(SimpleTestCase):
    def test_texto_multilinha_e_links_sem_enter(self):
        with patch.dict(
            os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(settings.BASE_DIR / ".local/browsers")}
        ):
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page()
                page.set_content("""<footer><div contenteditable='true' role='textbox'
                style='white-space:pre-wrap'></div></footer><script>window.enters=0;
                document.addEventListener('keydown',e=>{if(e.key==='Enter')window.enters++})</script>""")
                seletor = "footer [contenteditable=true]"
                campo = page.locator(seletor)
                texto = (
                    "Fictício: uma compra.\n\n➡️ Acesse:\nhttps://example.invalid\n\n• Opção: *Sim*."
                )
                # Não cola em campo sem foco, nem substitui conteúdo existente.
                with self.assertRaises(FalhaOperacao):
                    colar_no_campo(page, seletor, texto)
                campo.click()
                try:
                    colar_no_campo(page, seletor, texto)
                finally:
                    self.assertEqual(
                        [linha for linha in campo.inner_text().splitlines() if linha],
                        [linha for linha in texto.splitlines() if linha],
                    )
                self.assertEqual(page.evaluate("window.enters"), 0)
                with self.assertRaises(FalhaOperacao):
                    colar_no_campo(page, seletor, texto)
                browser.close()
