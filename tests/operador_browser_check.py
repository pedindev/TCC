"""Painel HTTP + worker + Playwright + catálogo, somente com páginas fictícias."""

import os
import queue
import re
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from playwright.sync_api import expect, sync_playwright

from apps.atendimento.fluxo import FluxoOperador
from apps.atendimento.navegador import Navegador
from apps.atendimento.simulacao import CAMPO_DEMO
from apps.catalogo.service import preparar_orientacao


class NavegadorControlado(Navegador):
    """O teste pede gestos do operador na thread dona da Page, nunca por fora dela."""

    def __init__(self, comandos, respostas):
        super().__init__(modo="simulacao", headless=True)
        self.comandos, self.respostas = comandos, respostas

    def status(self):
        self.conectar()
        try:
            comando = self.comandos.get_nowait()
        except queue.Empty:
            comando = ""
        if comando == "login":
            self.demo.siat.get_by_role("link", name="Concluir login fictício").click()
        elif comando == "focar":
            self.demo.whatsapp.bring_to_front()
            self.demo.whatsapp.locator(CAMPO_DEMO).click()
        elif comando == "fechar_whatsapp":
            self.demo.whatsapp.close()
        elif comando == "ler_colagem":
            self.respostas.put(
                (
                    self.demo.whatsapp.locator(CAMPO_DEMO).inner_text(),
                    self.demo.whatsapp.evaluate("window.enters"),
                )
            )
        return super().status()


@override_settings(APP_MODE="simulacao")
class OperadorBrowserCheck(StaticLiveServerTestCase):
    host = "127.0.0.1"
    serialized_rollback = True

    def setUp(self):
        super().setUp()
        env = patch.dict(
            os.environ,
            {"PLAYWRIGHT_BROWSERS_PATH": str(Path(settings.BASE_DIR) / ".local/browsers")},
        )
        env.start()
        self.addCleanup(env.stop)
        self.comandos, self.respostas = queue.Queue(), queue.Queue()
        self.erros_catalogo = []

        def catalogo(*args, **kwargs):
            try:
                return preparar_orientacao(*args, **kwargs)
            except Exception as erro:
                self.erros_catalogo.append(type(erro).__name__)
                raise

        self.fluxo = FluxoOperador(
            lambda: NavegadorControlado(self.comandos, self.respostas),
            modo="simulacao",
            contagem=2,
            catalogo=catalogo,
        )
        self.addCleanup(self.fluxo.fechar)
        runtime = patch("apps.atendimento.views.obter_fluxo", return_value=self.fluxo)
        runtime.start()
        self.addCleanup(runtime.stop)
        self.pw = sync_playwright().start()
        self.addCleanup(self.pw.stop)
        self.browser = self.pw.chromium.launch()
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page(viewport={"width": 1280, "height": 1050})
        self.page.goto(self.live_server_url + "/painel/")
        expect(self.page.locator("#siat-status")).to_contain_text("disponível", timeout=15000)

    def consultar(self, codigo):
        self.page.get_by_label("Código de rastreio", exact=True).fill(codigo)
        self.page.get_by_role("button", name="Consultar", exact=True).click()

    def novo(self):
        self.page.get_by_role("button", name="Novo atendimento").click()
        expect(self.page.locator("#mensagem")).to_have_value("")
        expect(self.page.locator("#rastreio")).to_be_enabled(timeout=10000)

    def test_consulta_comercializacao_contagem_colagem_sem_enter_e_novo(self):
        self.consultar("TESTE-COM")
        expect(self.page.locator("#situacao")).to_have_text("Retida", timeout=15000)
        expect(self.page.locator("#motivo")).to_have_text("Comercialização")
        self.assertEqual(self.erros_catalogo, [])
        campo = self.page.get_by_label("Mensagem completa para conferência", exact=True)
        texto = (
            "SIMULAÇÃO COM DADOS FICTÍCIOS\n\n"
            "Sua encomenda foi retida porque a fiscalização identificou indícios de que "
            "os produtos foram comprados para revenda."
        )
        expect(campo).to_have_value(texto)
        colar = self.page.get_by_role("button", name="Colar no WhatsApp", exact=True)
        expect(colar).to_be_visible()
        expect(colar).to_be_enabled(timeout=10000)
        self.page.reload()
        expect(self.page.locator("#mensagem")).to_have_value(texto)
        expect(self.page.locator("#consultar")).to_be_disabled()
        # Captura exclusivamente deste cenário fictício.
        saida = Path(settings.BASE_DIR) / ".local/validacao/painel-ficticio.png"
        saida.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(saida), full_page=True)
        # Exercita a colagem sem acessar a área de transferência do Windows.
        self.page.evaluate("""() => Object.defineProperty(navigator.clipboard, 'writeText', {
            value: async (texto) => { window.textoCopiado = texto; },
        })""")
        colar.click()
        expect(self.page.locator("#contagem")).to_be_visible()
        self.assertEqual(self.page.evaluate("window.textoCopiado"), texto)
        self.comandos.put("focar")
        expect(self.page.locator("#aviso")).to_have_text(
            "Texto colado. O envio é manual.", timeout=15000
        )
        self.comandos.put("ler_colagem")
        colado, enters = self.respostas.get(timeout=5)
        self.assertEqual(
            [linha for linha in colado.splitlines() if linha],
            [linha for linha in texto.splitlines() if linha],
        )
        self.assertEqual(enters, 0)
        expect(self.page.locator("#colar")).to_be_disabled()
        self.novo()
        expect(self.page.locator("#rastreio")).to_have_value("")
        expect(self.page.locator("#situacao")).to_have_text("Aguardando consulta")
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        # Digitar e sair do campo não pode apagar o rascunho a cada polling.
        self.page.locator("#rastreio").fill("TESTE-NF")
        self.page.locator("h1").click()
        self.page.wait_for_timeout(800)
        expect(self.page.locator("#rastreio")).to_have_value("TESTE-NF")

    def test_escolher_nota_avulsa_atualiza_texto_e_novo_limpa_opcoes(self):
        self.consultar("TESTE-NF")
        expect(self.page.locator("#opcoes-mensagens")).to_be_visible(timeout=15000)
        expect(self.page.locator("#mensagem-opcao")).to_be_enabled()
        primeira = self.page.locator("#mensagem").input_value()
        self.assertIn("fornecedor", primeira)
        self.page.locator("#mensagem-opcao").select_option("1")
        expect(self.page.locator("#mensagem")).to_have_value(
            re.compile("SOLICITE A NOTA FISCAL AVULSA")
        )
        expect(self.page.locator("#versao")).to_have_text("SAC-PEDIDO-NFA v5")
        self.page.reload()
        expect(self.page.locator("#mensagem-opcao")).to_have_value("1")
        expect(self.page.locator("#mensagem-opcao")).to_be_enabled()
        self.page.locator("#mensagem-opcao").select_option("0")
        expect(self.page.locator("#mensagem")).to_have_value(primeira)
        self.novo()
        expect(self.page.locator("#opcoes-mensagens")).to_be_hidden()

    def test_login_manual_recupera_e_vazio_repetido_fica_inconclusivo(self):
        self.consultar("TESTE-LOGIN")
        expect(self.page.locator("#aviso")).to_contain_text("Faça login", timeout=15000)
        expect(self.page.locator("#consultar")).to_be_disabled()
        self.comandos.put("login")
        expect(self.page.locator("#colar")).to_be_enabled(timeout=15000)
        texto = self.page.locator("#mensagem").input_value()
        self.assertTrue(texto.startswith("[SIMULAÇÃO"))
        self.assertIn("https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao", texto)
        self.novo()
        self.consultar("TESTE-VAZIO")
        expect(self.page.locator("#aviso")).to_contain_text("Faça login", timeout=15000)
        self.comandos.put("login")
        expect(self.page.locator("#aviso")).to_contain_text(
            "não pôde ser confirmada", timeout=15000
        )
        expect(self.page.locator("#situacao")).to_have_text("Não confirmada")
        expect(self.page.locator("#mensagem")).to_have_value("")
        expect(self.page.locator("#colar")).to_be_disabled()

    def test_whatsapp_indisponivel_e_excecoes_preservam_estado_honesto(self):
        self.consultar("TESTE-DIF")
        expect(self.page.locator("#colar")).to_be_enabled(timeout=15000)
        texto = self.page.locator("#mensagem").input_value()
        self.comandos.put("fechar_whatsapp")
        expect(self.page.locator("#whatsapp-status")).to_contain_text(
            "Aba não localizada", timeout=10000
        )
        expect(self.page.locator("#colar")).to_be_disabled()
        expect(self.page.locator("#mensagem")).to_have_value(texto)
        for codigo, aviso, situacao in [
            ("TESTE-DESCONHECIDO", "motivo não foi reconhecido", "Retida"),
            ("TESTE-LIBERADA", "não há orientação", "Liberada"),
            ("TESTE-CONEXAO", "Falha de conexão", "Não confirmada"),
            ("TESTE-DEMORA", "tempo de espera", "Não confirmada"),
        ]:
            self.novo()
            self.consultar(codigo)
            expect(self.page.locator("#aviso")).to_contain_text(aviso, timeout=10000)
            expect(self.page.locator("#situacao")).to_have_text(situacao)
            expect(self.page.locator("#mensagem")).to_have_value("")
