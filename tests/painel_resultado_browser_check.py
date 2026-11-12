"""Rolagem ao resultado com dados fictícios, inclusive sem foco inicial no documento."""

import os
from unittest.mock import patch

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from playwright.sync_api import sync_playwright


@override_settings(APP_MODE="navegador")
class PainelResultadoBrowserCheck(StaticLiveServerTestCase):
    host = "127.0.0.1"

    def test_resultado_sem_foco_rola_uma_vez_por_atendimento(self):
        estado = {
            "atendimento": "ficticio-1",
            "token": "ficticio",
            "fase": "consultando",
            "ocupado": True,
            "rastreio": "FICTICIO",
            "situacao": "",
            "motivo": "",
            "mensagem": "",
            "versao": "",
            "aviso_catalogo": "",
            "aviso": "Consultando",
            "acao": "",
            "erro": "",
            "pode_colar": False,
            "colagem_tentada": False,
            "segundos": 0,
            "modo": "navegador",
            "sistemas": {
                n: {"estado": "disponivel", "texto": "Fictício"} for n in ("siat", "whatsapp")
            },
        }
        with (
            patch.dict(
                os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(settings.BASE_DIR / ".local/browsers")}
            ),
            sync_playwright() as pw,
        ):
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width": 1100, "height": 700})
                page.route("**/api/estado/", lambda r: r.fulfill(json=estado))
                page.add_init_script("Object.defineProperty(document,'hasFocus',{value:()=>false})")
                page.goto(self.live_server_url)
                page.wait_for_function(
                    "document.querySelector('#aviso').textContent==='Consultando'"
                )
                self.assertEqual(page.evaluate("window.scrollY"), 0)
                estado.update(
                    fase="pronto",
                    ocupado=False,
                    situacao="retida",
                    motivo="FICTÍCIO",
                    mensagem="Orientação fictícia\n\n" * 30,
                )
                verificar = """() => {
                    const r=document.getElementById('resultado-titulo').getBoundingClientRect();
                    return r.top>=0 && r.top<100 && r.bottom<=innerHeight
                      && document.activeElement.id==='resultado-titulo';
                }"""
                page.wait_for_function(verificar)
                # O polling não deve contrariar a rolagem manual após posicionar o resultado.
                page.evaluate("window.scrollTo(0,0)")
                page.wait_for_timeout(1500)
                self.assertEqual(page.evaluate("window.scrollY"), 0)
                estado.update(
                    atendimento="ficticio-2",
                    fase="consultando",
                    ocupado=True,
                    situacao="",
                    mensagem="",
                    aviso="Segunda consulta",
                )
                page.wait_for_function(
                    "document.querySelector('#aviso').textContent==='Segunda consulta'"
                )
                estado.update(
                    fase="pronto",
                    ocupado=False,
                    situacao="retida",
                    mensagem="Segunda orientação fictícia\n\n" * 30,
                )
                page.wait_for_function(verificar)
            finally:
                browser.close()
