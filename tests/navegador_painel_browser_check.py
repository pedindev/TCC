"""O processo é descoberto pelo painel, sem abrir sistemas ou perfis reais."""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from playwright.sync_api import sync_playwright

from apps.atendimento.desktop import TransporteWindows


class NavegadorPainelCheck(SimpleTestCase):
    def test_vinculo_pelo_painel_e_abas_em_outras_janelas(self):
        canais = [None]
        if Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe").exists():
            canais.append("msedge")
        with (
            patch.dict(
                os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(settings.BASE_DIR / ".local/browsers")}
            ),
            sync_playwright() as pw,
        ):
            for canal in canais:
                with self.subTest(canal=canal or "chromium"):
                    browser = pw.chromium.launch(headless=False, channel=canal)
                    transporte = None
                    try:
                        processos = browser.new_browser_cdp_session().send(
                            "SystemInfo.getProcessInfo"
                        )
                        pid = next(
                            int(p["id"]) for p in processos["processInfo"] if p["type"] == "browser"
                        )
                        transporte = TransporteWindows(processo_teste=pid)
                        contexto = browser.new_context()
                        outra_janela = browser.new_context()

                        def rota(r):
                            paginas = {
                                "https://web.whatsapp.com/": "WhatsApp",
                                "https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml": (
                                    "SIAT - Fictício"
                                ),
                                "http://127.0.0.1:8000/": "Painel • MVP",
                                "https://example.invalid/": "Painel • MVP",
                            }
                            titulo = paginas.get(r.request.url)
                            if titulo is None:
                                return r.abort()
                            return r.fulfill(
                                content_type="text/html; charset=utf-8",
                                body=f"<title>{titulo}</title><h1>Conteúdo fictício</h1>",
                            )

                        contexto.route("**/*", rota)
                        outra_janela.route("**/*", rota)
                        wa = outra_janela.new_page()
                        wa.goto("https://web.whatsapp.com/")
                        siat = contexto.new_page()
                        siat.goto("https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml")
                        with ThreadPoolExecutor(max_workers=1) as executor:

                            def status(transporte=transporte, siat=siat):
                                futuro = executor.submit(transporte.chamar, "status")
                                ate = time.monotonic() + 18
                                while not futuro.done() and time.monotonic() < ate:
                                    siat.wait_for_timeout(50)
                                return futuro.result(timeout=1)

                            self.assertEqual(
                                status()["whatsapp"]["estado"], "painel_nao_identificado"
                            )
                            painel = contexto.new_page()
                            painel.goto("https://example.invalid/")
                            self.assertEqual(
                                status()["whatsapp"]["estado"], "painel_nao_identificado"
                            )
                            painel.goto("http://127.0.0.1:8000/")
                            self.assertEqual(status()["whatsapp"]["estado"], "localizada")
                            wa.bring_to_front()
                            self.assertEqual(status()["siat"]["estado"], "localizada")
                            painel.close()
                            self.assertEqual(
                                status()["whatsapp"]["estado"], "painel_nao_identificado"
                            )
                    finally:
                        if transporte:
                            transporte.fechar()
                        browser.close()
