"""Retorno nativo do SIAT fictício ao painel, sem consultar registros reais."""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from playwright.sync_api import sync_playwright

from apps.atendimento.desktop import TransporteWindows


class RetornoPainelBrowserCheck(SimpleTestCase):
    def test_mesma_janela_e_janela_separada_com_variacoes_do_painel(self):
        with (
            patch.dict(
                os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(settings.BASE_DIR / ".local/browsers")}
            ),
            sync_playwright() as pw,
        ):
            browser = pw.chromium.launch(headless=False)
            transporte = None
            try:
                processos = browser.new_browser_cdp_session().send("SystemInfo.getProcessInfo")
                pid = next(p["id"] for p in processos["processInfo"] if p["type"] == "browser")
                transporte = TransporteWindows(processo_teste=pid)

                def rota(r):
                    if r.request.url.startswith("https://webas.sefaz.pi.gov.br/siatweb/"):
                        html = '<title>SIAT - Fictício</title><a href="#">Sair</a>'
                    elif r.request.url in (
                        "http://127.0.0.1:8000/",
                        "http://127.0.0.1:8000/painel/",
                    ):
                        html = "<title>Painel • MVP</title><h1>Atendimento fictício</h1>"
                    else:
                        return r.abort()
                    return r.fulfill(content_type="text/html; charset=utf-8", body=html)

                contexto = browser.new_context()
                contexto.route("**/*", rota)
                siat = contexto.new_page()
                siat.goto("https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml")
                painel_inicial = contexto.new_page()
                painel_inicial.goto("http://127.0.0.1:8000/")
                with ThreadPoolExecutor(max_workers=1) as executor:

                    def chamar(acao, referencia=""):
                        futuro = executor.submit(transporte.chamar, acao, referencia)
                        ate = time.monotonic() + 18
                        while not futuro.done() and time.monotonic() < ate:
                            siat.wait_for_timeout(50)
                        return futuro.result(timeout=1)

                    referencia = chamar("status")["siat"]["referencia"]
                    painel_inicial.close()
                    for separado, caminho, titulo in (
                        (False, "/", "Painel • MVP"),
                        (False, "/painel/", "Uso da memória em Painel • MVP: 20 MB"),
                        (True, "/painel/", "Painel • MVP"),
                    ):
                        with self.subTest(separado=separado, caminho=caminho):
                            janela = browser.new_context() if separado else contexto
                            if separado:
                                janela.route("**/*", rota)
                            painel = janela.new_page()
                            painel.goto("http://127.0.0.1:8000" + caminho)
                            painel.evaluate("titulo=>document.title=titulo", titulo)
                            painel.bring_to_front()
                            self.assertEqual(chamar("ativar", referencia), {"resultado": "ok"})
                            self.assertTrue(siat.evaluate("document.hasFocus()"))
                            self.assertEqual(chamar("retornar_painel"), {"resultado": "ok"})
                            self.assertTrue(painel.evaluate("document.hasFocus()"))
                            self.assertEqual(painel.url, "http://127.0.0.1:8000" + caminho)
                            painel.close()
                            if separado:
                                janela.close()
            finally:
                if transporte:
                    transporte.fechar()
                browser.close()
