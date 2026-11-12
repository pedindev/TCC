"""Clique real no painel → clipboard → worker → Ctrl+V nativo, sem envio.

Chromium temporário e helper restrito ao seu PID. WhatsApp inteiramente fictício;
não abre SIAT nem acessa conversas ou o navegador pessoal.
"""

import os
from unittest.mock import patch

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from playwright.sync_api import expect, sync_playwright

from apps.atendimento.desktop import NavegadorDesktop, TransporteWindows
from apps.atendimento.fluxo import FluxoOperador
from apps.catalogo.service import preparar_orientacao
from apps.siat.resultado import Resultado

WHATSAPP = """<title>WhatsApp</title>
<input aria-label="Pesquisar mensagens" id="pesquisa">
<footer><div role="textbox" aria-label="Digite uma mensagem para Contato fictício"
contenteditable="true" style="white-space:pre-wrap;min-height:150px;border:1px solid"><p
class="selectable-text copyable-text" dir="ltr" style="margin:0"><br></p></div></footer>
<script>window.envios=0;window.colagens=0;
document.addEventListener('keydown',e=>{if(e.key==='Enter')window.envios++});
document.addEventListener('paste',()=>window.colagens++);</script>"""


@override_settings(APP_MODE="navegador")
class WhatsAppDesktopBrowserCheck(StaticLiveServerTestCase):
    host = "127.0.0.1"

    def test_botao_copia_catalogo_e_cola_no_paragrafo_sem_enter(self):
        mensagem = preparar_orientacao(Resultado("retida", "simei", True))
        with (
            patch.dict(
                os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(settings.BASE_DIR / ".local/browsers")}
            ),
            sync_playwright() as pw,
        ):
            browser = pw.chromium.launch(headless=False)
            fluxo = None
            try:
                sessao = browser.new_browser_cdp_session()
                processos = sessao.send("SystemInfo.getProcessInfo")["processInfo"]
                pid = next(int(p["id"]) for p in processos if p["type"] == "browser")
                contexto = browser.new_context(permissions=["clipboard-read", "clipboard-write"])

                def rota(r):
                    if r.request.url.startswith("https://web.whatsapp.com/"):
                        return r.fulfill(content_type="text/html; charset=utf-8", body=WHATSAPP)
                    if r.request.url.startswith(self.live_server_url + "/"):
                        return r.continue_()
                    return r.abort()

                contexto.route("**/*", rota)
                wa = contexto.new_page()
                wa.goto("https://web.whatsapp.com/")
                fluxo = FluxoOperador(
                    lambda: NavegadorDesktop(TransporteWindows(processo_teste=pid)),
                    modo="navegador",
                    contagem=8,
                )
                s = fluxo.snapshot()
                # Somente esta etapa: resultado e catálogo preparados, sem consultar SIAT.
                fluxo._atualizar(
                    s["atendimento"],
                    fase="pronto",
                    situacao="retida",
                    motivo="SIMEI",
                    mensagem=mensagem["texto"],
                    versao=mensagem["versao"],
                    pode_colar=True,
                )
                with patch("apps.atendimento.views.obter_fluxo", return_value=fluxo):
                    painel = contexto.new_page()
                    painel.goto(self.live_server_url)
                    expect(painel.locator("#colar")).to_be_enabled(timeout=20000)
                    expect(painel.locator("#mensagem")).to_have_value(mensagem["texto"])
                    # Sem cópia confirmada, o botão não pode agendar uma colagem.
                    painel.evaluate("""() => {
                        window.escreverOriginal=navigator.clipboard.writeText.bind(navigator.clipboard);
                        Object.defineProperty(navigator.clipboard,'writeText',{
                            configurable:true,value:()=>Promise.reject(new Error('negado fictício'))
                        });
                    }""")
                    painel.locator("#colar").click()
                    expect(painel.locator("#copia-status")).to_contain_text("não permitiu copiar")
                    painel.wait_for_timeout(1100)
                    expect(painel.locator("#copia-status")).to_be_visible()
                    self.assertEqual(fluxo.snapshot()["fase"], "pronto")
                    self.assertEqual(wa.evaluate("window.colagens"), 0)
                    painel.evaluate("""() => Object.defineProperty(navigator.clipboard,'writeText',{
                        configurable:true,value:window.escreverOriginal
                    })""")
                    painel.locator("#colar").click()
                    expect(painel.locator("#contagem")).to_be_visible()
                    # A cópia precisa existir antes de abrir o campo de destino.
                    self.assertEqual(
                        painel.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n"),
                        mensagem["texto"],
                    )
                    wa.bring_to_front()
                    wa.locator("footer p").click()
                    expect(painel.locator("#aviso")).to_have_text(
                        "Texto colado. O envio é manual.", timeout=20000
                    )
                    colado = wa.get_by_role("textbox", name="Digite uma mensagem", exact=False)
                    self.assertEqual(colado.inner_text().replace("\r\n", "\n"), mensagem["texto"])
                    self.assertEqual(wa.locator("#pesquisa").input_value(), "")
                    self.assertEqual(wa.evaluate("window.colagens"), 1)
                    self.assertEqual(wa.evaluate("window.envios"), 0)
                    expect(painel.locator("#colar")).to_be_disabled()
            finally:
                if fluxo:
                    fluxo.fechar()
                browser.close()
