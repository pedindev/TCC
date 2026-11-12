"""Teste opcional com menu fictício; não acessa nem reproduz o DOM real do SIAT."""

import os
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase
from playwright.sync_api import sync_playwright

from apps.siat.consulta import FalhaPesquisaSiat, pesquisar_rastreio
from apps.siat.estado import LoginSiatNecessario, TelaConsultaIndisponivel
from apps.siat.navegacao import FalhaNavegacaoSiat, abrir_consulta_notificacao
from apps.siat.recuperacao import ResultadoConsulta, consultar_com_recuperacao
from apps.siat.sessao import EstadoSessao, estado_sessao, monitorar_sessao

MENU = """
<style>
  li { list-style: none; width: 240px; }
  li > ul { display: none; }
  li:hover > ul { display: block; }
  button { width: 220px; height: 40px; }
</style>
<ul><li><button>Trânsito</button>
  <ul><li><button>Notificação Correios</button>
    <ul>
      <li><button onclick="window.emissoes++">Emitir Notificação</button></li>
      <li><button onclick="window.consultas++">Consultar Notificação</button></li>
    </ul>
  </li></ul>
</li></ul>
<script>window.emissoes = 0; window.consultas = 0;</script>
"""

FORMULARIO = """
<h1>Consultar Notificação</h1>
<select><option>CPF/CNPJ</option><option>Cód. Rastreio</option></select>
<input value="RASTREIO-ANTERIOR">
<button onclick="window.pesquisas.push({
    tipo: document.querySelector('select').value,
    codigo: document.querySelector('input').value
})">Consultar</button>
<p>Nenhuma notificação encontrada!</p>
<script>window.pesquisas = [];</script>
"""


class SiatNavigationCheck(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        browser_path = str(Path(settings.BASE_DIR) / ".local" / "browsers")
        env = patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": browser_path})
        env.start()
        cls.addClassCleanup(env.stop)
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        cls.browser = cls.playwright.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.page = self.browser.new_page()
        self.page.set_default_timeout(1500)
        self.addCleanup(self.page.context.close)
        self.page.set_content(MENU)

    def test_percurso_consulta_sem_emitir_notificacao(self):
        self.page.set_content(MENU + FORMULARIO.replace("<h1>Consultar Notificação</h1>", ""))
        abrir_consulta_notificacao(self.page)
        self.assertEqual(self.page.evaluate("window.consultas"), 1)
        self.assertEqual(self.page.evaluate("window.emissoes"), 0)

    def test_menu_ausente_interrompe_sem_expor_pagina(self):
        self.page.set_content("<p>MARCADOR-PRIVADO</p><input aria-label='Senha'>")
        with self.assertRaises(FalhaNavegacaoSiat) as failure:
            abrir_consulta_notificacao(self.page, timeout_ms=200)
        self.assertIn("Trânsito", str(failure.exception))
        self.assertNotIn("MARCADOR-PRIVADO", str(failure.exception))

    def test_consulta_ambigua_nao_escolhe_primeiro_item(self):
        self.page.set_content(
            MENU.replace("<script>", "<button>Consultar Notificação</button><script>")
        )
        with self.assertRaises(FalhaNavegacaoSiat):
            abrir_consulta_notificacao(self.page, timeout_ms=500)
        self.assertEqual(self.page.evaluate("window.consultas"), 0)
        self.assertEqual(self.page.evaluate("window.emissoes"), 0)

    def test_timeout_zero_nao_permite_espera_infinita(self):
        with self.assertRaises(ValueError):
            abrir_consulta_notificacao(self.page, timeout_ms=0)

    def test_duas_pesquisas_reutilizam_tela_e_substituem_rastreio(self):
        self.page.set_content(FORMULARIO)
        for codigo in ("FICTICIO-01", "FICTICIO-02"):
            self.assertIsNone(pesquisar_rastreio(self.page, codigo))
        self.assertEqual(
            self.page.evaluate("window.pesquisas"),
            [
                {"tipo": "Cód. Rastreio", "codigo": "FICTICIO-01"},
                {"tipo": "Cód. Rastreio", "codigo": "FICTICIO-02"},
            ],
        )

    def test_formulario_ambiguo_nao_altera_nem_pesquisa(self):
        self.page.set_content(FORMULARIO + "<input value='OUTRO-CAMPO'>")
        with self.assertRaises(TelaConsultaIndisponivel):
            pesquisar_rastreio(self.page, "FICTICIO-01", timeout_ms=200)
        self.assertEqual(self.page.locator("select").input_value(), "CPF/CNPJ")
        self.assertEqual(self.page.evaluate("window.pesquisas"), [])

    def test_login_interrompe_sem_preencher_credenciais(self):
        self.page.route(
            "**/*",
            lambda route: route.fulfill(
                body="<input value=''><input type='password' value=''><button>Ok</button>",
                content_type="text/html",
            ),
        )
        self.page.goto("https://webas.sefaz.pi.gov.br/siatweb/faces/login.xhtml")
        for acao in (
            lambda: abrir_consulta_notificacao(self.page),
            lambda: pesquisar_rastreio(self.page, "FICTICIO-01"),
        ):
            with self.assertRaisesMessage(LoginSiatNecessario, "Entre novamente no navegador"):
                acao()
        self.assertEqual(
            self.page.locator("input").evaluate_all("inputs => inputs.map(input => input.value)"),
            ["", ""],
        )

    def test_redirecionamento_para_login_apos_menu_exibe_aviso(self):
        self.page.route(
            "**/*",
            lambda route: route.fulfill(body="<p>Login fictício</p>", content_type="text/html"),
        )
        menu_com_login = MENU.replace(
            "window.consultas++",
            "location.href='https://webas.sefaz.pi.gov.br/siatweb/faces/login.xhtml'",
        )
        self.page.set_content(menu_com_login)
        with self.assertRaisesMessage(LoginSiatNecessario, "Entre novamente no navegador"):
            abrir_consulta_notificacao(self.page, timeout_ms=500)

    def test_opcao_rastreio_ausente_nao_consulta_com_outro_filtro(self):
        self.page.set_content(FORMULARIO.replace("<option>Cód. Rastreio</option>", ""))
        with self.assertRaises(FalhaPesquisaSiat) as failure:
            pesquisar_rastreio(self.page, "MARCADOR-PRIVADO", timeout_ms=200)
        self.assertNotIn("MARCADOR-PRIVADO", str(failure.exception))
        self.assertEqual(self.page.get_by_role("textbox").input_value(), "RASTREIO-ANTERIOR")
        self.assertEqual(self.page.evaluate("window.pesquisas"), [])

    def test_rastreio_vazio_ou_com_espacos_nao_aciona_consulta(self):
        self.page.set_content(FORMULARIO)
        for codigo in ("", "   ", "FICTICIO 01", "FICTICIO\n01"):
            with self.subTest(codigo=codigo), self.assertRaises(ValueError):
                pesquisar_rastreio(self.page, codigo)
        self.assertEqual(self.page.evaluate("window.pesquisas"), [])

    def preparar_recuperacao(
        self, *, segundo_vazio=False, atualiza=True, inicio=False, expira=False
    ):
        """Todo tráfego interceptado: não consulta nenhum serviço real."""
        self.logins = 0
        self.avisos = []
        self.voltas_inicio = 0
        login_url = "https://webas.sefaz.pi.gov.br/siatweb/faces/login.xhtml"
        index_url = "https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml"

        def responder(route):
            if "login.xhtml" in route.request.url:
                self.logins += 1
                corpo = f"""<input><input type="password">
                <button onclick="location.href='{index_url}'">Login manual fictício</button>"""
            else:
                mensagem = (
                    "Nenhuma Notificação encontrada!"
                    if self.logins == 0 or segundo_vazio
                    else "Resultado fictício atualizado"
                )
                acao = "this.closest('form').outerHTML=this.closest('form').outerHTML"
                if not atualiza:
                    acao = "void(0)"
                if expira and self.logins == 0:
                    acao = f"location.href='{login_url}'"
                corpo = f"""<a href='{login_url}'><img alt='Sair'> Sair</a>
                <form id="frmConsultar" onsubmit="return false">
                  <select><option>Cód. Rastreio</option></select><input>
                  <button type="button" onclick="{acao}">Consultar</button>
                  <div id="frmConsultar:dTableNotificacao">{mensagem}</div>
                </form>"""
                if inicio and self.logins:
                    self.voltas_inicio += 1
                    corpo = corpo.replace(
                        '<form id="frmConsultar"', '<form hidden id="frmConsultar"'
                    )
                    corpo += """<p>Bem-vindo(a) a Central de Atendimento ao Contribuinte.</p>
                    <button>Trânsito</button><button>Notificação Correios</button>
                    <button onclick="document.querySelector('form').hidden=false">
                    Consultar Notificação</button>"""
            route.fulfill(body=corpo, content_type="text/html; charset=utf-8")

        self.page.route("**/*", responder)
        self.page.goto(index_url)

    def login_manual_ficticio(self, mensagem):
        self.avisos.append(mensagem)
        if mensagem.startswith("Faça login"):
            self.assertEqual(estado_sessao(self.page), EstadoSessao.LOGIN)
            self.assertEqual(self.page.locator('input[type="password"]').input_value(), "")
            self.page.get_by_role("button", name="Login manual fictício").click()

    def test_vazio_sai_aguarda_login_e_repete_mesmo_codigo(self):
        self.preparar_recuperacao(inicio=True)
        with patch(
            "apps.siat.recuperacao.pesquisar_rastreio", wraps=pesquisar_rastreio
        ) as pesquisa:
            resultado = consultar_com_recuperacao(
                self.page, "FICTICIO-01", self.login_manual_ficticio
            )
        self.assertEqual(resultado, ResultadoConsulta.PROSSEGUIR_LEITURA)
        self.assertEqual(self.logins, 1)
        self.assertEqual(self.voltas_inicio, 1)
        self.assertEqual(pesquisa.call_count, 2)
        self.assertEqual([c.args[1] for c in pesquisa.call_args_list], ["FICTICIO-01"] * 2)
        self.assertFalse(any("FICTICIO-01" in aviso for aviso in self.avisos))

    def test_vazio_repetido_interrompe_sem_loop_de_logout(self):
        self.preparar_recuperacao(segundo_vazio=True)
        resultado = consultar_com_recuperacao(self.page, "FICTICIO-01", self.login_manual_ficticio)
        self.assertEqual(resultado, ResultadoConsulta.CONFERIR_MANUALMENTE)
        self.assertEqual(self.logins, 1)
        self.assertIn("não confirma ausência", self.avisos[-1])

    def test_vazio_antigo_sem_atualizacao_nao_provoca_logout(self):
        self.preparar_recuperacao(atualiza=False)
        with self.assertRaises(FalhaPesquisaSiat):
            consultar_com_recuperacao(self.page, "FICTICIO-01", self.avisos.append, timeout_ms=250)
        self.assertEqual(self.logins, 0)
        self.assertEqual(self.avisos, [])

    def test_sem_login_manual_expira_espera_sem_preencher_campos(self):
        self.preparar_recuperacao()
        with self.assertRaises(LoginSiatNecessario):
            consultar_com_recuperacao(
                self.page, "FICTICIO-01", self.avisos.append, timeout_login_ms=100
            )
        self.assertEqual(self.logins, 1)
        self.assertEqual(
            self.page.locator("input").evaluate_all("els => els.map(e => e.value)"), ["", ""]
        )

    def test_login_inicial_aguarda_operador(self):
        self.preparar_recuperacao()
        self.page.get_by_role("link", name="Sair Sair").click()
        resultado = consultar_com_recuperacao(self.page, "FICTICIO-01", self.login_manual_ficticio)
        self.assertEqual(resultado, ResultadoConsulta.PROSSEGUIR_LEITURA)
        self.assertEqual(sum(a.startswith("Faça login") for a in self.avisos), 1)
        self.assertEqual(self.logins, 1)

    def test_sessao_expira_ao_consultar_e_repete_apos_login(self):
        self.preparar_recuperacao(expira=True)
        resultado = consultar_com_recuperacao(
            self.page, "FICTICIO-01", self.login_manual_ficticio, timeout_ms=1000
        )
        self.assertEqual(resultado, ResultadoConsulta.PROSSEGUIR_LEITURA)
        self.assertEqual(self.logins, 1)
        self.assertEqual(sum(a.startswith("Faça login") for a in self.avisos), 1)

    def test_tela_desconhecida_nao_presume_login(self):
        self.preparar_recuperacao()
        self.page.set_content("<p>Outra tela</p>")
        with self.assertRaises(TelaConsultaIndisponivel):
            consultar_com_recuperacao(self.page, "FICTICIO-01", self.avisos.append)
        self.assertEqual(self.logins, 0)

    def test_monitor_detecta_login_e_retorno_sem_consultar(self):
        self.preparar_recuperacao()
        estados = []

        def informar(estado):
            estados.append(estado)
            if len(estados) == 1:
                self.page.get_by_role("link", name="Sair Sair").click()
            elif len(estados) == 2:
                self.page.get_by_role("button", name="Login manual fictício").click()

        monitorar_sessao(self.page, informar, lambda: len(estados) == 3, intervalo_ms=100)
        self.assertEqual(
            estados, [EstadoSessao.CONSULTA, EstadoSessao.LOGIN, EstadoSessao.CONSULTA]
        )
