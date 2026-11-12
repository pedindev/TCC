"""Extensão MV3 real em perfil temporário; páginas externas 100% interceptadas."""

import os
import shutil
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from playwright.sync_api import expect, sync_playwright

from apps.atendimento.extensao import NavegadorExtensao
from apps.atendimento.fluxo import FluxoOperador
from apps.atendimento.ponte import PonteExtensao

SIAT = "https://webas.sefaz.pi.gov.br/siatweb/faces/"
WA = """<div id="main"><p>CONVERSA-FICTICIA-NAO-EXPORTAR</p><footer>
<div role="textbox" contenteditable="true" style="width:500px;min-height:100px"></div>
</footer></div><script>window.envios=0; document.addEventListener('keydown', e=>{
if(e.key==='Enter') window.envios++});</script>"""
CONSULTA = """<a href="login.xhtml">Sair</a><form id="frmConsultar">
<select><option>Cód. Rastreio</option></select><input type="text">
<button type="button" onclick="const f=this.closest('form');
f.replaceWith(f.cloneNode(true))">Consultar</button>
<table id="frmConsultar:dTableNotificacao"><tr><td>MARCADOR</td></tr></table></form>"""


@override_settings(APP_MODE="navegador")
class ExtensaoBrowserCheck(StaticLiveServerTestCase):
    host = "127.0.0.1"

    def test_abas_individuais_recuperacao_e_colagem_sem_envio(self):
        ponte = PonteExtensao()
        browser_path = str(Path(settings.BASE_DIR) / ".local" / "browsers")
        with tempfile.TemporaryDirectory(prefix="mvp-extensao-") as pasta:
            extensao = Path(pasta) / "extensao"
            shutil.copytree(Path(settings.BASE_DIR) / "extensao", extensao)
            porta = self.live_server_url.rsplit(":", 1)[1]
            for nome in ("background.js", "painel.js"):
                arquivo = extensao / nome
                arquivo.write_text(
                    arquivo.read_text(encoding="utf-8").replace('"8000"', f'"{porta}"'),
                    encoding="utf-8",
                )
            with (
                patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": browser_path}),
                patch("apps.atendimento.views.ponte", ponte),
                patch("apps.atendimento.extensao.ponte", ponte),
                sync_playwright() as pw,
            ):
                fluxo = FluxoOperador(NavegadorExtensao, modo="navegador")
                try:
                    with patch("apps.atendimento.views.obter_fluxo", return_value=fluxo):
                        contexto = pw.chromium.launch_persistent_context(
                            str(Path(pasta) / "perfil"),
                            channel="chromium",
                            headless=True,
                            args=[
                                f"--disable-extensions-except={extensao}",
                                f"--load-extension={extensao}",
                            ],
                        )
                        try:
                            self._verificar(contexto, ponte)
                        finally:
                            contexto.close()
                finally:
                    fluxo.fechar()

    def _verificar(self, contexto, ponte):
        vazio = True

        def interceptar(rota):
            url = rota.request.url
            if url.startswith(self.live_server_url):
                return rota.continue_()
            if url.startswith(SIAT):
                if "login.xhtml" in url:
                    html = '<a href="index.xhtml">Concluir login fictício</a>'
                else:
                    html = CONSULTA.replace(
                        "MARCADOR",
                        "Nenhuma Notificação encontrada!" if vazio else "RESULTADO-FICTICIO",
                    )
                return rota.fulfill(status=200, content_type="text/html; charset=utf-8", body=html)
            if url.startswith("https://web.whatsapp.com/"):
                return rota.fulfill(status=200, content_type="text/html; charset=utf-8", body=WA)
            return rota.abort()

        contexto.route("**/*", interceptar)
        wa = contexto.new_page()
        wa.goto("https://web.whatsapp.com/")
        worker = (
            contexto.service_workers[0]
            if contexto.service_workers
            else contexto.wait_for_event("serviceworker")
        )
        worker.evaluate("""async () => {
          const [aba] = await chrome.tabs.query({url: 'https://web.whatsapp.com/*'});
          await chrome.windows.create({tabId: aba.id});
        }""")
        painel = contexto.new_page()
        painel.goto(self.live_server_url)
        expect(painel.locator("#whatsapp-status")).to_contain_text(
            "WhatsApp conectado", timeout=15000
        )
        expect(painel.locator("#siat-status")).to_contain_text("Aba não localizada")
        siat = contexto.new_page()
        siat.goto(SIAT + "login.xhtml")
        expect(painel.locator("#siat-status")).to_contain_text("Faça login", timeout=10000)
        siat.get_by_text("Concluir login fictício").click()
        expect(painel.locator("#siat-status")).to_contain_text("Consulta disponível", timeout=10000)
        duplicada = contexto.new_page()
        duplicada.goto("https://web.whatsapp.com/")
        expect(painel.locator("#whatsapp-status")).to_contain_text("mais de uma aba", timeout=10000)
        expect(painel.locator("#siat-status")).to_contain_text("Consulta disponível")
        duplicada.close()
        expect(painel.locator("#whatsapp-status")).to_contain_text(
            "WhatsApp conectado", timeout=10000
        )

        painel.locator("#rastreio").fill("TESTE-FICTICIO")
        painel.locator("#consultar").click()
        expect(siat.get_by_text("Concluir login fictício")).to_be_visible(timeout=15000)
        expect(painel.locator("#aviso")).to_contain_text("Faça login", timeout=10000)
        vazio = False
        siat.get_by_text("Concluir login fictício").click()
        expect(painel.locator("#acao")).to_contain_text("leitura", timeout=15000)
        self.assertEqual(siat.locator('input[type="text"]').input_value(), "TESTE-FICTICIO")

        # Comando pela ponte real, sem promover catálogo rascunho no produto.
        wa.bring_to_front()
        wa.locator('[role="textbox"]').click()
        resultados = []
        thread = threading.Thread(
            target=lambda: resultados.append(
                ponte.executar("whatsapp", "colar", "TEXTO FICTÍCIO\n\nhttps://example.org/")
            )
        )
        thread.start()
        try:
            expect(wa.locator('[role="textbox"]')).to_contain_text("TEXTO FICTÍCIO", timeout=12000)
            # Faz o event loop do navegador processar o retorno da extensão.
            painel.wait_for_timeout(1200)
        finally:
            thread.join(timeout=10)
        self.assertEqual(resultados, ["ok"])
        self.assertEqual(wa.evaluate("window.envios"), 0)
        # Nem repetir o comando nem preencher um campo já ocupado é permitido.
        texto_original = wa.locator('[role="textbox"]').inner_text()
        resultado = worker.evaluate("""async () => {
          const [aba] = await chrome.tabs.query({url: 'https://web.whatsapp.com/*'});
          const comando = {id:'teste-repetido', sistema:'whatsapp', aba:aba.id,
            acao:'colar', valor:'NAO INSERIR', limite:Date.now()/1000+8};
          return [await executar(comando), await executar(comando)];
        }""")
        self.assertEqual(resultado, ["sem_foco", "falha"])
        self.assertEqual(wa.locator('[role="textbox"]').inner_text(), texto_original)
        self.assertNotIn("CONVERSA-FICTICIA-NAO-EXPORTAR", str(ponte.estados))
        wa.close()
        expect(painel.locator("#whatsapp-status")).to_contain_text(
            "Aba não localizada", timeout=10000
        )
        expect(painel.locator("#siat-status")).to_contain_text("Consulta disponível")
