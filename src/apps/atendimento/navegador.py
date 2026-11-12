"""Monitor de abas existentes; não abre sites ou janelas no modo de atendimento."""

from time import monotonic
from urllib.parse import urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from apps.atendimento.erros import FalhaOperacao
from apps.atendimento.simulacao import CAMPO_DEMO, PaginasFicticias
from apps.siat.service import consultar
from apps.siat.sessao import EstadoSessao, estado_sessao
from apps.whatsapp.colagem import colar_no_campo

HOSTS = {"siat": "webas.sefaz.pi.gov.br", "whatsapp": "web.whatsapp.com"}
SEM_CONEXAO = (
    "Navegador não conectado. Verifique a conexão local com o navegador; tentaremos novamente."
)


def disponibilidade(estado, texto):
    return {"estado": estado, "texto": texto}


class Navegador:
    def __init__(self, *, modo="preparacao", endpoint="", campo_whatsapp="", headless=False):
        self.modo, self.endpoint, self.campo = modo, endpoint, campo_whatsapp
        self.headless = headless
        self.pw = self.browser = self.demo = None
        self.proxima_conexao = 0.0

    def conectar(self):
        if self.browser and self.browser.is_connected():
            return
        if self.modo == "preparacao" or (self.modo == "navegador" and not self.endpoint):
            return
        if monotonic() < self.proxima_conexao:
            return
        if not self.pw:
            self.pw = sync_playwright().start()
        if self.modo == "simulacao":
            self.browser = self.pw.chromium.launch(headless=self.headless)
            self.demo = PaginasFicticias(self.browser.new_context(service_workers="block"))
            self.campo = CAMPO_DEMO
        else:
            url = urlsplit(self.endpoint)
            if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost", "::1"}:
                raise ValueError("A conexão do navegador deve usar HTTP em loopback.")
            try:
                self.browser = self.pw.chromium.connect_over_cdp(self.endpoint, timeout=1500)
            except PlaywrightError:
                self.browser = None
                self.proxima_conexao = monotonic() + 5
                raise
            self.proxima_conexao = 0.0

    def _abas(self):
        """Uma leitura por ciclo, em todos os contextos/janelas do navegador conectado."""
        grupos = {host: [] for host in HOSTS.values()}
        if self.browser and self.browser.is_connected():
            for contexto in self.browser.contexts:
                for page in contexto.pages:
                    if not page.is_closed():
                        host = urlsplit(page.url).hostname
                        if host in grupos:
                            grupos[host].append(page)
        return grupos

    def pagina(self, host):
        self.conectar()
        paginas = self._abas().get(host, [])
        return paginas[0] if len(paginas) == 1 else None

    @staticmethod
    def _status_abas(paginas):
        if not paginas:
            return disponibilidade(
                "nao_aberto", "Aba não localizada. Abra o site no navegador conectado."
            )
        if len(paginas) > 1:
            return disponibilidade(
                "verificar", "Há mais de uma aba deste sistema. Deixe apenas a que será usada."
            )
        return None

    def _status_siat(self, page):
        estado = estado_sessao(page)
        if estado == EstadoSessao.LOGIN:
            return disponibilidade("login", "Aberto. Faça login no navegador.")
        if estado in (EstadoSessao.INICIO, EstadoSessao.CONSULTA):
            return disponibilidade("disponivel", "Aberto e disponível para consultar.")
        return disponibilidade(
            "verificar", "Aberto. Confira o login e a tela Consultar Notificação."
        )

    def _status_whatsapp(self, page):
        if self.campo:
            campo = page.locator(self.campo)
            if campo.count() == 1 and campo.is_visible():
                return disponibilidade("disponivel", "Aberto. Confira a conversa antes de colar.")
        return disponibilidade(
            "verificar",
            "Aberto. Confira o login e abra uma conversa no navegador."
            if self.campo
            else "Aberto. O campo de mensagem ainda precisa ser configurado.",
        )

    def status(self):
        try:
            self.conectar()
            abas = self._abas()
        except (PlaywrightError, ValueError):
            aviso = disponibilidade("indisponivel", SEM_CONEXAO)
            return {"siat": aviso, "whatsapp": aviso.copy()}
        if not self.browser or not self.browser.is_connected():
            aviso = disponibilidade(
                "indisponivel", "Conexão desativada." if self.modo == "preparacao" else SEM_CONEXAO
            )
            return {"siat": aviso, "whatsapp": aviso.copy()}
        estados = {}
        for nome, verificar in (("siat", self._status_siat), ("whatsapp", self._status_whatsapp)):
            paginas = abas[HOSTS[nome]]
            estado = self._status_abas(paginas)
            if estado is None:
                try:
                    estado = verificar(paginas[0])
                except PlaywrightError:
                    estado = disponibilidade(
                        "verificar", "A página está mudando. Aguarde a próxima verificação."
                    )
            estados[nome] = estado
        return estados

    def consultar(self, codigo, avisar, verificar):
        page = self.pagina(HOSTS["siat"])
        if page is None:
            raise FalhaOperacao(
                "conexao",
                "O SIAT não está disponível no navegador conectado.",
                "Abra uma única aba do SIAT no navegador conectado e faça login.",
            )
        kwargs = {}
        if self.demo:
            self.demo.preparar(codigo)
            kwargs["leitor"] = self.demo.ler
        return consultar(
            codigo, page=page, avisar=avisar, verificar_continuacao=verificar, **kwargs
        )

    def colar(self, texto):
        page = self.pagina(HOSTS["whatsapp"])
        if not page:
            raise FalhaOperacao(
                "whatsapp_indisponivel",
                "O WhatsApp está indisponível. A orientação foi mantida.",
                "Abra uma única aba do WhatsApp no navegador conectado e faça login.",
            )
        colar_no_campo(page, self.campo, texto)

    def fechar(self):
        if self.demo and self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()
