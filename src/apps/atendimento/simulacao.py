"""Cenários declaradamente fictícios. Todas as requisições são interceptadas."""

from html import escape

from apps.atendimento.erros import FalhaOperacao
from apps.siat.resultado import Resultado

CENARIOS = {
    "TESTE-COM": "comercializacao",
    "TESTE-SIM": "simei",
    "TESTE-DIF": "difal",
    "TESTE-NF": "sem_nota_fiscal",
    "TESTE-IRF": "irregularidades_fiscais",
    "TESTE-LOGIN": "comercializacao",
    "TESTE-VAZIO": "",
    "TESTE-DESCONHECIDO": "nao_mapeado",
    "TESTE-LIBERADA": "",
    "TESTE-CONEXAO": "",
    "TESTE-DEMORA": "",
}
SIAT_URL = "https://webas.sefaz.pi.gov.br/siatweb/faces/index.xhtml"
LOGIN_URL = "https://webas.sefaz.pi.gov.br/siatweb/faces/login.xhtml"
WHATSAPP_URL = "https://web.whatsapp.com/"
CAMPO_DEMO = 'footer [role="textbox"][contenteditable="true"]'
ESTILO = """<meta charset='utf-8'><style>
body{font:18px system-ui;max-width:900px;margin:40px auto;background:#f4f6f5;color:#243d38}
button,input,select{font:inherit;padding:12px;margin:8px}footer{margin-top:60px}
[contenteditable]{white-space:pre-wrap;background:white;border:2px solid #58736c;padding:20px}
</style><h1>SIMULAÇÃO LOCAL — somente dados fictícios</h1>"""


class PaginasFicticias:
    def __init__(self, contexto):
        self.codigo = "TESTE-COM"
        self.recuperado = False
        contexto.route("**/*", self.responder)
        self.siat = contexto.new_page()
        self.siat.goto(SIAT_URL)
        self.whatsapp = contexto.new_page()
        self.whatsapp.goto(WHATSAPP_URL)

    def responder(self, route):
        url = route.request.url
        if url == WHATSAPP_URL:
            corpo = """<h2>WhatsApp fictício · Conversa de teste</h2>
            <p>Nada é enviado. Clique no campo abaixo durante a contagem regressiva.</p>
            <footer><div role="textbox" aria-label="Mensagem de teste"
            contenteditable="true"></div></footer>
            <p id="envios">Envios automáticos: 0</p>
            <script>window.enters=0;document.addEventListener('keydown',e=>{
            if(e.key==='Enter'){window.enters++;e.preventDefault()}})</script>"""
        elif url == LOGIN_URL:
            corpo = f"""<h2>Login fictício do SIAT</h2>
            <p>Não informe usuário ou senha. Este botão representa o login manual.</p>
            <a href='{SIAT_URL}?retorno=1'>Concluir login fictício</a>"""
        elif url.startswith(SIAT_URL):
            if "retorno=1" in url:
                self.recuperado = True
            corpo = f"""<a href='{LOGIN_URL}'>Sair</a><form id="frmConsultar"
                onsubmit="return false"><h2>Consultar Notificação</h2>
                <select><option>Cód. Rastreio</option></select><input aria-label="Rastreio">
                <button type="button" onclick="fetch('/resposta-ficticia').then(r=>r.text())
                .then(html=>document.getElementById('frmConsultar').outerHTML=html)">
                Consultar</button><div id="frmConsultar:dTableNotificacao">
                Nenhuma Notificação encontrada!</div></form>"""
        elif url.endswith("/resposta-ficticia"):
            vazio = self.codigo == "TESTE-VAZIO" or (
                self.codigo == "TESTE-LOGIN" and not self.recuperado
            )
            motivo = CENARIOS[self.codigo]
            situacao = "liberada" if self.codigo == "TESTE-LIBERADA" else "retida"
            resultado = (
                "Nenhuma Notificação encontrada!"
                if vazio
                else (
                    f'<span data-codigo="{escape(self.codigo)}" '
                    f'data-situacao="{situacao}" data-motivo="{motivo}">Resultado fictício</span>'
                )
            )
            corpo = f"""<form id="frmConsultar" onsubmit="return false">
                <select><option>Cód. Rastreio</option></select><input aria-label="Rastreio">
                <button type="button" onclick="fetch('/resposta-ficticia').then(r=>r.text())
                .then(html=>document.getElementById('frmConsultar').outerHTML=html)">
                Consultar</button><div id="frmConsultar:dTableNotificacao">{resultado}</div>
                </form>"""
            route.fulfill(body=corpo, content_type="text/html; charset=utf-8")
            return
        else:
            route.abort()
            return
        route.fulfill(body=ESTILO + corpo, content_type="text/html; charset=utf-8")

    def preparar(self, codigo):
        if codigo not in CENARIOS:
            raise FalhaOperacao(
                "codigo_ficticio",
                "Este modo aceita apenas os códigos de teste indicados.",
                "Use TESTE-COM, TESTE-SIM, TESTE-DIF, TESTE-NF ou TESTE-IRF.",
            )
        self.codigo = codigo
        self.recuperado = False
        if codigo in {"TESTE-CONEXAO", "TESTE-DEMORA"}:
            raise FalhaOperacao(
                "conexao" if codigo == "TESTE-CONEXAO" else "demora",
                "Falha de conexão simulada."
                if codigo == "TESTE-CONEXAO"
                else "A consulta excedeu o tempo de espera (simulação).",
                "Confira o navegador e inicie um novo atendimento para tentar novamente.",
            )

    def ler(self, page, codigo):
        item = page.locator("[data-codigo]")
        if item.count() != 1 or item.get_attribute("data-codigo") != codigo:
            return Resultado("", confirmado=False)
        return Resultado(
            item.get_attribute("data-situacao"), item.get_attribute("data-motivo"), confirmado=True
        )
