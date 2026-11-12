"""UI Automation nativa em Chromium temporário com páginas inteiramente fictícias.

O helper fica restrito ao PID criado pelo teste; não observa nem controla Chrome pessoal.
"""

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from playwright.sync_api import sync_playwright

from apps.atendimento.desktop import TransporteWindows

SIAT = "https://webas.sefaz.pi.gov.br/siatweb/faces/"
FORM = """<title>SIAT - Teste isolado</title><a href="login.xhtml">Sair</a>
<form id="frmConsultar"><select aria-label="Tipo"><option value="">Pesquisar por</option>
<option value="cpf">CPF/CNPJ</option><option value="rastreio">Cód. Rastreio</option></select>
<input aria-label="Rastreio"><button type="button" onclick="window.pesquisas.push({
tipo:document.querySelector('select').value,codigo:document.querySelector('input').value});
const f=this.closest('form');
f.replaceWith(f.cloneNode(true))">Consultar</button>
<table><tr><td>Nenhuma Notificação encontrada!</td></tr></table></form>
<script>window.pesquisas=[];</script>"""
WA = """<title>WhatsApp</title><div role="textbox"
aria-label="Digite uma mensagem para Contato fictício"
contenteditable="true" style="width:500px;min-height:150px;border:1px solid"></div>
<script>window.atrasoColagem=0;document.addEventListener('paste', e=>{
if(window.atrasoColagem){e.preventDefault();const texto=e.clipboardData.getData('text/plain');
setTimeout(()=>document.querySelector('[role="textbox"]').innerText=texto,window.atrasoColagem);}});
window.envios=0; document.addEventListener('keydown', e=>{
if(e.key==='Enter') window.envios++});</script>"""
TABELA = """<table id="frmConsultar:dTableNotificacao"><thead><tr>
<th>Núm. Termo</th><th>Cód. Rastreio</th>
<th>CPF/CNPJ</th><th>Nome</th><th>Data Emissão</th><th>Opções</th></tr></thead><tbody>
<tr><td>FICTICIO</td><td>OUTRO-FICTICIO</td><td>FICTICIO</td><td>FICTICIO</td><td>FICTICIO</td>
<td><button id="frmConsultar:dTableNotificacao:0:j_idt47" type="submit" title="ui-button"
role="button" aria-disabled="false" onclick="window.cliquesDetalhe.push('errado');return false">
<span class="ui-button-icon-primary ui-icon ui-icon-zoomin"></span>
<span class="ui-button-text ui-c">ui-button</span></button></td></tr>
<tr><td>FICTICIO</td><td>TESTE-FICTICIO</td><td>FICTICIO</td><td>FICTICIO</td><td>FICTICIO</td>
<td><button id="frmConsultar:dTableNotificacao:1:j_idt47" type="submit" title="ui-button"
role="button" aria-disabled="false" onclick="window.cliquesDetalhe.push('correto');
dlgVisualizar.show();return false">
<span class="ui-button-icon-primary ui-icon ui-icon-zoomin"></span>
<span class="ui-button-text ui-c">ui-button</span></button></td></tr>
</tbody></table>"""
FORM_RESULTADO = (
    FORM.replace("<table><tr><td>Nenhuma Notificação encontrada!</td></tr></table>", TABELA)
    + """<button onclick="window.cliquesDetalhe.push('fora')">ui-button</button>
<section id="dlgVisualizar" hidden><form id="frmVisualizar">Detalhes fictícios</form></section>
<script>window.cliquesDetalhe=[];window.dlgVisualizar={show(){
document.getElementById('dlgVisualizar').hidden=false;
setTimeout(()=>{document.getElementById('frmVisualizar').innerHTML=
'<label for="frmVisualizar:j_idt68">Inf. Adicionais:</label>'+
'<input id="frmVisualizar:j_idt68" name="frmVisualizar:j_idt68" '+
'type="text" readonly maxlength="250" value="SIMEI - ICMS fictício">';},200);
}};</script>"""
)


class DesktopBrowserCheck(SimpleTestCase):
    def test_abas_foco_consulta_atualizacao_e_colagem(self):
        caminho = str(Path(settings.BASE_DIR) / ".local" / "browsers")
        with patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": caminho}), sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            transporte = None
            try:
                sessao = browser.new_browser_cdp_session()
                processos = sessao.send("SystemInfo.getProcessInfo")["processInfo"]
                pid = next(int(p["id"]) for p in processos if p["type"] == "browser")
                transporte = TransporteWindows(processo_teste=pid)
                contexto = browser.new_context()

                def rota(r):
                    if r.request.url.startswith(SIAT):
                        html = (
                            (
                                "<title>SIAT - Login fictício</title>"
                                '<a href="index.xhtml">Login fictício</a>'
                            )
                            if "login.xhtml" in r.request.url
                            else FORM_RESULTADO
                            if "resultado.xhtml" in r.request.url
                            else FORM
                        )
                    elif r.request.url.startswith("https://web.whatsapp.com/"):
                        html = WA
                    elif r.request.url == "http://127.0.0.1:8000/":
                        html = "<title>Painel • MVP</title><h1>Painel fictício</h1>"
                    else:
                        return r.abort()
                    return r.fulfill(status=200, content_type="text/html; charset=utf-8", body=html)

                contexto.route("**/*", rota)
                contexto_wa = browser.new_context()
                contexto_wa.route("**/*", rota)
                wa = contexto_wa.new_page()
                wa.goto("https://web.whatsapp.com/")
                siat = contexto.new_page()
                siat.goto(SIAT + "index.xhtml")
                with ThreadPoolExecutor(max_workers=1) as executor:

                    def chamar(acao, referencia="", valor=""):
                        futuro = executor.submit(transporte.chamar, acao, referencia, valor)
                        limite = time.monotonic() + 18
                        while not futuro.done() and time.monotonic() < limite:
                            siat.wait_for_timeout(50)
                        return futuro.result(timeout=1)

                    estados = chamar("status")
                    self.assertIn(estados.get("whatsapp", {}).get("estado"), ("localizada",))
                    self.assertIn(estados.get("siat", {}).get("estado"), ("localizada", "consulta"))
                    referencia = estados["siat"]["referencia"]
                    wa.bring_to_front()
                    self.assertEqual(chamar("ativar", referencia), {"resultado": "ok"})
                    self.assertEqual(chamar("estado", referencia), {"resultado": "consulta"})
                    self.assertEqual(siat.get_by_role("combobox").input_value(), "")
                    self.assertEqual(
                        chamar("consultar", referencia, "TESTE-FICTICIO"), {"resultado": "vazio"}
                    )
                    self.assertEqual(siat.get_by_role("textbox").input_value(), "TESTE-FICTICIO")
                    self.assertEqual(
                        siat.evaluate("window.pesquisas"),
                        [{"tipo": "rastreio", "codigo": "TESTE-FICTICIO"}],
                    )
                    atual = chamar("status")
                    self.assertEqual(atual["siat"]["referencia"], referencia, str(atual))
                    self.assertEqual(chamar("sair", referencia), {"resultado": "ok"})
                    self.assertEqual(chamar("estado", referencia), {"resultado": "login"})
                    # Login manual fictício; o helper não preenche credenciais.
                    siat.get_by_text("Login fictício").click()
                    siat.goto(SIAT + "resultado.xhtml")
                    painel = contexto.new_page()
                    painel.goto("http://127.0.0.1:8000/")
                    painel.bring_to_front()
                    self.assertEqual(chamar("ativar", referencia), {"resultado": "ok"})
                    self.assertEqual(
                        chamar("detalhes", referencia, "TESTE-FICTICIO"),
                        {"resultado": "resultado_nao_confirmado"},
                    )
                    self.assertEqual(
                        chamar("consultar", referencia, "TESTE-FICTICIO"),
                        {"resultado": "atualizado"},
                    )
                    self.assertEqual(
                        chamar("detalhes", referencia, "TESTE-FICTICIO"),
                        {"resultado": "detalhes_acionados"},
                    )
                    self.assertEqual(siat.evaluate("window.cliquesDetalhe"), ["correto"])
                    self.assertTrue(siat.locator("#frmVisualizar").is_visible())
                    self.assertEqual(
                        chamar("retencao", referencia, "TESTE-FICTICIO"),
                        {"resultado": "retencao_lida", "descricao": "SIMEI - ICMS fictício"},
                    )
                    self.assertEqual(
                        chamar("retencao", referencia, "TESTE-FICTICIO"),
                        {"resultado": "resultado_nao_confirmado"},
                    )
                    self.assertEqual(
                        chamar("detalhes", referencia, "TESTE-FICTICIO"),
                        {"resultado": "resultado_nao_confirmado"},
                    )
                    siat.evaluate("""() => {
                        document.getElementById('dlgVisualizar').hidden=true;
                        const t=document.querySelector('tbody');
                        t.appendChild(t.lastElementChild.cloneNode(true));}""")
                    self.assertEqual(
                        chamar("consultar", referencia, "TESTE-FICTICIO"),
                        {"resultado": "atualizado"},
                    )
                    self.assertEqual(
                        chamar("detalhes", referencia, "TESTE-FICTICIO"),
                        {"resultado": "linha_ambigua"},
                    )
                    self.assertEqual(siat.evaluate("window.cliquesDetalhe"), ["correto"])
                    self.assertEqual(chamar("retornar_painel"), {"resultado": "ok"})
                    self.assertTrue(painel.evaluate("document.hasFocus()"))
                    self.assertEqual(
                        chamar("retornar_painel"), {"resultado": "painel_indisponivel"}
                    )
                    wa.bring_to_front()
                    wa.get_by_role("textbox").click()
                    wa.evaluate("window.atrasoColagem=700")
                    colagem = chamar("colar", valor="TEXTO FICTÍCIO\n\nhttps://example.org/")
                    self.assertEqual(
                        colagem, {"resultado": "ok"}, repr(wa.get_by_role("textbox").inner_text())
                    )
                    self.assertEqual(
                        re.sub(r"\n{3,}", "\n\n", wa.get_by_role("textbox").inner_text()),
                        "TEXTO FICTÍCIO\n\nhttps://example.org/",
                    )
                    self.assertEqual(wa.evaluate("window.envios"), 0)
                    self.assertEqual(
                        chamar("colar", valor="NAO REPETIR"), {"resultado": "campo_ocupado"}
                    )
                    wa.close()
                    limite = time.monotonic() + 5
                    while time.monotonic() < limite:
                        estado = chamar("status")["whatsapp"]["estado"]
                        if estado == "ausente":
                            break
                        siat.wait_for_timeout(200)
                    self.assertEqual(estado, "ausente")
            finally:
                if transporte:
                    transporte.fechar()
                browser.close()
