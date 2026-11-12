from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings
from playwright.sync_api import Error as PlaywrightError

from apps.atendimento.navegador import Navegador


class ConexaoTests(SimpleTestCase):
    @override_settings(APP_MODE="navegador")
    def test_painel_informa_monitoramento_sem_exigir_mesma_janela(self):
        resposta = self.client.get("/painel/")
        self.assertContains(resposta, "inclusive em janelas diferentes")
        self.assertNotContains(resposta, "Antes de começar")
        self.assertNotContains(resposta, 'target="_blank"')
        self.assertNotContains(resposta, "Simulação local")
        self.assertNotContains(resposta, "Carregar sem compactação")
        self.assertContains(resposta, "sem usar mouse ou teclado")

    def test_conexao_falhou_nao_pede_login_como_se_estivesse_conectado(self):
        navegador = Navegador(modo="navegador", endpoint="http://127.0.0.1:9222")
        navegador.conectar = MagicMock(side_effect=PlaywrightError("Falha fictícia"))
        estados = navegador.status()
        self.assertEqual(estados["siat"]["estado"], "indisponivel")
        self.assertIn("conexão local", estados["whatsapp"]["texto"])
        self.assertNotIn("Falha fictícia", str(estados))

    def test_conectado_sem_abas_orienta_abrir_aba(self):
        navegador = Navegador(modo="navegador")
        navegador.browser = MagicMock()
        navegador.browser.is_connected.return_value = True
        navegador.browser.contexts = []
        estados = navegador.status()
        self.assertIn("Aba não localizada", estados["siat"]["texto"])

    def test_preparacao_nao_tenta_acessar_sistemas(self):
        navegador = Navegador(modo="preparacao")
        estados = navegador.status()
        self.assertIn("Conexão desativada", estados["siat"]["texto"])
        self.assertIsNone(navegador.pw)

    @staticmethod
    def pagina_falsa(url):
        pagina = MagicMock()
        pagina.url = url
        pagina.is_closed.return_value = False
        return pagina

    def test_abertura_fechamento_e_login_em_contextos_distintos_sem_criar_abas(self):
        navegador = Navegador(modo="navegador")
        navegador.browser = MagicMock()
        navegador.browser.is_connected.return_value = True
        siat = self.pagina_falsa("https://webas.sefaz.pi.gov.br/siatweb/faces/login.xhtml")
        wa = self.pagina_falsa("https://web.whatsapp.com/")
        contexto1, contexto2 = MagicMock(), MagicMock()
        contexto1.pages, contexto2.pages = [], []
        navegador.browser.contexts = [contexto1, contexto2]
        self.assertEqual(navegador.status()["siat"]["estado"], "nao_aberto")
        contexto1.pages, contexto2.pages = [siat], [wa]
        with patch.object(navegador, "_abas", wraps=navegador._abas) as inventario:
            estados = navegador.status()
            self.assertEqual(inventario.call_count, 1)
        self.assertEqual(estados["siat"]["estado"], "login")
        self.assertEqual(estados["whatsapp"]["estado"], "verificar")
        siat.url = "https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml"
        self.assertEqual(navegador.status()["siat"]["estado"], "disponivel")
        wa.is_closed.return_value = True
        estados = navegador.status()
        self.assertEqual(estados["whatsapp"]["estado"], "nao_aberto")
        self.assertEqual(estados["siat"]["estado"], "disponivel")
        for contexto in (contexto1, contexto2):
            contexto.new_page.assert_not_called()
        for pagina in (siat, wa):
            pagina.goto.assert_not_called()
            pagina.close.assert_not_called()

    def test_abas_duplicadas_nao_sao_tratadas_como_fechadas(self):
        navegador = Navegador(modo="navegador")
        navegador.browser = MagicMock()
        navegador.browser.is_connected.return_value = True
        contexto = MagicMock()
        contexto.pages = [self.pagina_falsa("https://web.whatsapp.com/") for _ in range(2)]
        navegador.browser.contexts = [contexto]
        self.assertIn("mais de uma aba", navegador.status()["whatsapp"]["texto"])
        self.assertIsNone(navegador.pagina("web.whatsapp.com"))

    def test_reconecta_sem_loop_de_tentativas_e_sem_abrir_navegador(self):
        navegador = Navegador(modo="navegador", endpoint="http://127.0.0.1:9222")
        navegador.pw = MagicMock()
        browser = MagicMock()
        browser.is_connected.return_value = True
        browser.contexts = []
        conectar = navegador.pw.chromium.connect_over_cdp
        conectar.side_effect = [PlaywrightError("Falha fictícia"), browser]
        with patch("apps.atendimento.navegador.monotonic", return_value=10):
            self.assertEqual(navegador.status()["siat"]["estado"], "indisponivel")
        with patch("apps.atendimento.navegador.monotonic", return_value=12):
            navegador.status()
        self.assertEqual(conectar.call_count, 1)
        with patch("apps.atendimento.navegador.monotonic", return_value=16):
            self.assertEqual(navegador.status()["siat"]["estado"], "nao_aberto")
        self.assertEqual(conectar.call_count, 2)
        navegador.pw.chromium.launch.assert_not_called()

    def test_falha_no_whatsapp_nao_apaga_estado_do_siat(self):
        navegador = Navegador(modo="navegador", campo_whatsapp="campo-ficticio")
        navegador.browser = MagicMock()
        navegador.browser.is_connected.return_value = True
        contexto = MagicMock()
        siat = self.pagina_falsa("https://webas.sefaz.pi.gov.br/siatweb/faces/login.xhtml")
        wa = self.pagina_falsa("https://web.whatsapp.com/")
        wa.locator.side_effect = PlaywrightError("Página fechando")
        contexto.pages = [siat, wa]
        navegador.browser.contexts = [contexto]
        estados = navegador.status()
        self.assertEqual(estados["siat"]["estado"], "login")
        self.assertEqual(estados["whatsapp"]["estado"], "verificar")
