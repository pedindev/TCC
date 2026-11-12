"""Janela SIAT fictícia: fechar detalhes só ao preparar uma nova consulta."""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from playwright.sync_api import sync_playwright

from apps.atendimento.desktop import TransporteWindows

HTML = """<title>SIAT - Teste isolado de detalhes</title>
<a href="#" onclick="window.saidas++;return false">Sair</a>
<form><select aria-label="Tipo"><option>Cód. Rastreio</option></select>
<input aria-label="Rastreio"><button type="button" onclick="window.pesquisas++;
this.closest('form').replaceWith(this.closest('form').cloneNode(true))">Consultar</button>
<p>Nenhuma Notificação encontrada!</p></form>
<section role="dialog" id="janela-ficticia" aria-label="Informações fictícias">
<header><a href="#" role="button" onclick="window.fora++;return false">
<span class="ui-icon ui-icon-closethick">close</span></a></header>
<form id="frmVisualizar"><label for="frmVisualizar:j_idt68">Inf. Adicionais:</label>
<input id="frmVisualizar:j_idt68" readonly value="SIMEI FICTÍCIO">
<button id="frmVisualizar:j_idt98" name="frmVisualizar:j_idt98" type="submit" role="button"
aria-disabled="false" onclick="window.fechamentos++;
document.getElementById('janela-ficticia').hidden=true;return false">
<span class="ui-button-text">Fechar</span></button></form></section>
<button onclick="window.fora++">Fechar</button>
<script>window.saidas=0;window.fechamentos=0;window.fora=0;window.pesquisas=0;</script>"""


class SiatDesktopDialogCheck(SimpleTestCase):
    def test_fechar_so_detalhes_e_continuar_consulta(self):
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
                contexto = browser.new_context()

                def rota(r):
                    if r.request.url.startswith("https://webas.sefaz.pi.gov.br/siatweb/"):
                        return r.fulfill(content_type="text/html; charset=utf-8", body=HTML)
                    return r.abort()

                contexto.route("**/*", rota)
                page = contexto.new_page()
                page.goto("https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml")
                with ThreadPoolExecutor(max_workers=1) as executor:

                    def chamar(acao, referencia="", valor=""):
                        futuro = executor.submit(transporte.chamar, acao, referencia, valor)
                        ate = time.monotonic() + 18
                        while not futuro.done() and time.monotonic() < ate:
                            page.wait_for_timeout(50)
                        return futuro.result(timeout=1)

                    estado = chamar("status")["siat"]
                    self.assertEqual(estado["estado"], "detalhes")
                    referencia = estado["referencia"]
                    self.assertEqual(page.evaluate("window.fechamentos"), 0)
                    self.assertEqual(chamar("ativar", referencia), {"resultado": "ok"})
                    self.assertEqual(page.evaluate("window.fechamentos"), 0)
                    self.assertEqual(
                        chamar("preparar_consulta", referencia), {"resultado": "detalhes_fechados"}
                    )
                    self.assertEqual(chamar("estado", referencia), {"resultado": "consulta"})
                    self.assertEqual(
                        chamar("preparar_consulta", referencia), {"resultado": "sem_detalhes"}
                    )
                    self.assertEqual(
                        chamar("consultar", referencia, "RASTREIO-FICTICIO"), {"resultado": "vazio"}
                    )
                    self.assertEqual(page.evaluate("window.pesquisas"), 1)
                    self.assertEqual(page.evaluate("window.fechamentos"), 1)
                    self.assertEqual(page.evaluate("window.saidas+window.fora"), 0)
                    page.evaluate("""() => {
                        document.getElementById('janela-ficticia').hidden=false;
                        const botao=document.getElementById('frmVisualizar:j_idt98');
                        botao.parentNode.appendChild(botao.cloneNode(true));
                    }""")
                    self.assertEqual(
                        chamar("preparar_consulta", referencia), {"resultado": "fechar_ambiguo"}
                    )
                    self.assertEqual(page.evaluate("window.fechamentos"), 1)
            finally:
                if transporte:
                    transporte.fechar()
                browser.close()
