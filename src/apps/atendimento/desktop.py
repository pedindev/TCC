"""Transporte local para UI Automation do Windows; somente dados transitórios."""

import json
import os
import queue
import subprocess
import threading
import time
from pathlib import Path

from apps.atendimento.erros import FalhaOperacao
from apps.siat.estado import LoginSiatNecessario
from apps.siat.recuperacao import ResultadoConsulta, recuperar_com_motor
from apps.siat.resultado import resultado_da_retencao
from apps.siat.sessao import EstadoSessao


class TransporteWindows:
    def __init__(self, *, processo_teste=None):
        self.processo = None
        self.respostas = queue.Queue()
        self.processo_teste = processo_teste
        self.sequencia = 0

    def iniciar(self):
        if self.processo and self.processo.poll() is None:
            return
        if os.name != "nt":
            raise RuntimeError("Windows necessário.")
        script = Path(__file__).resolve().parents[3] / "native" / "desktop.ps1"
        sistema = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        powershell = sistema / "System32/WindowsPowerShell/v1.0/powershell.exe"
        argumentos = [
            str(powershell),
            "-NoProfile",
            "-NonInteractive",
            "-STA",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
        ]
        if self.processo_teste:
            argumentos += ["-ProcessoTeste", str(self.processo_teste)]
        self.respostas = queue.Queue()
        self.processo = subprocess.Popen(
            argumentos,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        processo, respostas = self.processo, self.respostas

        def receber():
            try:
                for linha in processo.stdout:
                    respostas.put(json.loads(linha))
            except (ValueError, OSError):
                pass
            finally:
                respostas.put(None)

        threading.Thread(target=receber, daemon=True, name="mvp-uia-resposta").start()

    def chamar(self, acao, referencia="", valor="", *, prazo=12):
        try:
            self.iniciar()
            self.sequencia += 1
            pedido = {
                "id": self.sequencia,
                "acao": acao,
                "referencia": referencia,
                "valor": valor,
                "limite": int((time.time() + prazo) * 1000),
            }
            self.processo.stdin.write(json.dumps(pedido, ensure_ascii=True) + "\n")
            self.processo.stdin.flush()
            resposta = self.respostas.get(timeout=prazo + 2)
            if not isinstance(resposta, dict) or resposta.get("id") != self.sequencia:
                raise RuntimeError("Resposta inválida.")
            return resposta["dados"]
        except Exception:
            self.fechar()
            raise FalhaOperacao(
                "colagem_incerta" if acao == "colar" else "conexao",
                "Não foi possível concluir a comunicação com o navegador do painel.",
                "Confira o navegador e o painel. Antes de repetir uma colagem, confira a mensagem.",
            ) from None

    def fechar(self):
        if self.processo:
            if self.processo.poll() is None:
                self.processo.kill()  # Somente o helper criado e possuído por esta instância.
                self.processo.wait(timeout=5)
            for fluxo in (self.processo.stdin, self.processo.stdout):
                fluxo.close()
            self.processo = None


ESTADOS = {
    "painel_nao_identificado": (
        "verificar",
        "Navegador do painel ainda não identificado. Deixe esta aba visível. "
        "Se persistir, os controles do navegador precisam ser verificados.",
    ),
    "painel_ambiguo": (
        "verificar",
        "Há mais de um painel aberto. Deixe visível o painel que será usado.",
    ),
    "ausente": (
        "nao_aberto",
        "Aba não localizada no navegador deste painel. Abra o site nesse navegador.",
    ),
    "duplicada": ("verificar", "Há mais de uma aba deste sistema. Deixe apenas a que será usada."),
    "localizada": ("disponivel", "Aba localizada. O login será conferido ao acessar a página."),
    "login": ("login", "Faça login no próprio site e mantenha essa aba aberta."),
    "consulta": ("disponivel", "SIAT aberto. Tela de consulta reconhecida."),
    "inicio": ("disponivel", "SIAT aberto. Página inicial reconhecida."),
    "detalhes": (
        "disponivel",
        "SIAT aberto. Os detalhes serão fechados ao iniciar outra consulta.",
    ),
    "erro": (
        "indisponivel",
        "Não foi possível verificar o navegador deste painel. Volte à aba do painel e aguarde.",
    ),
}


class MotorDesktop:
    def __init__(self, navegador, referencia, verificar):
        self.navegador, self.referencia, self.verificar = navegador, referencia, verificar
        self.resultado = None

    def acionar(self, acao, valor=""):
        self.verificar()
        dados = self.navegador.transporte.chamar(acao, self.referencia, valor)
        resultado = dados.get("resultado")
        if resultado == "login" and acao not in {"estado", "preparar_consulta"}:
            raise LoginSiatNecessario("Faça login no SIAT.")
        if resultado in {"falha", "foco", "demora", "incerto"}:
            raise FalhaOperacao(
                "demora" if resultado == "demora" else "falha_consulta",
                "A automação parou porque não conseguiu confirmar a tela ou o foco do SIAT.",
                "Abra a aba do SIAT, confira o login e inicie um novo atendimento. "
                "Durante a consulta, aguarde sem usar mouse ou teclado.",
            )
        self.navegador.ultimo = 0
        return resultado

    def estado(self):
        return {
            "login": EstadoSessao.LOGIN,
            "inicio": EstadoSessao.INICIO,
            "consulta": EstadoSessao.CONSULTA,
        }.get(self.acionar("estado"), EstadoSessao.DESCONHECIDA)

    def abrir(self):
        self.acionar("abrir")

    def preparar_consulta(self):
        resultado = self.acionar("preparar_consulta")
        if resultado not in {"sem_detalhes", "detalhes_fechados", "login"}:
            raise FalhaOperacao(
                "fechar_detalhes",
                "Não foi possível fechar com segurança a janela de informações do SIAT.",
                "Use o botão Fechar dos detalhes e inicie uma nova consulta. "
                "Não é necessário sair da conta.",
            )

    def pesquisar(self, codigo):
        self.resultado = self.acionar("consultar", codigo)

    def vazia(self):
        return self.resultado == "vazio"

    def sair(self):
        self.acionar("sair")

    def abrir_detalhes(self, codigo):
        if self.resultado != "atualizado":
            raise FalhaOperacao(
                "inconclusivo",
                "A resposta da consulta não foi confirmada.",
                "Confira a consulta no SIAT antes de abrir os detalhes.",
            )
        resultado = self.acionar("detalhes", codigo)
        if resultado != "detalhes_acionados":
            raise FalhaOperacao(
                "detalhes_indisponiveis",
                "Não foi possível identificar uma única lupa na linha do rastreio consultado.",
                "Confira a tabela no SIAT. É necessário confirmar o botão e a estrutura da linha "
                "antes de continuar automaticamente.",
            )

    def pausar(self):
        time.sleep(0.5)

    def ler_retencao(self, codigo):
        self.verificar()
        dados = self.navegador.transporte.chamar("retencao", self.referencia, codigo)
        self.verificar()
        if dados.get("resultado") == "login":
            raise LoginSiatNecessario("Faça login no SIAT.")
        if dados.get("resultado") != "retencao_lida":
            raise FalhaOperacao(
                "inconclusivo",
                "Não foi possível confirmar o campo Inf. Adicionais desta consulta.",
                "Confira os detalhes no SIAT. Se o campo não carregou, tente um novo atendimento.",
            )
        return resultado_da_retencao(dados.get("descricao"))


class NavegadorDesktop:
    def __init__(self, transporte=None):
        self.transporte = transporte or TransporteWindows()
        self.ultimo = 0
        self.estados = {}

    def status(self):
        if time.monotonic() - self.ultimo >= 3:
            try:
                self.estados = self.transporte.chamar("status")
            except FalhaOperacao:
                self.estados = {}
            self.ultimo = time.monotonic()
        return {
            nome: dict(
                zip(
                    ("estado", "texto"),
                    ESTADOS.get(self.estados.get(nome, {}).get("estado"), ESTADOS["erro"]),
                    strict=True,
                )
            )
            for nome in ("siat", "whatsapp")
        }

    def consultar(self, codigo, avisar, verificar):
        self.ultimo = 0
        self.status()
        referencia = self.estados.get("siat", {}).get("referencia")
        if not referencia:
            raise FalhaOperacao(
                "conexao",
                "Não foi possível localizar uma única aba do SIAT.",
                "Abra o SIAT no mesmo navegador deste painel e deixe uma única aba desse sistema.",
            )
        avisar(
            "Vou trazer o SIAT para frente. Aguarde sem usar mouse ou teclado durante a consulta."
        )
        time.sleep(0.8)
        motor = MotorDesktop(self, referencia, verificar)
        motor.acionar("ativar")
        avisar("Preparando a consulta. Se houver detalhes abertos, vou fechar essa janela.")
        motor.preparar_consulta()
        resultado = recuperar_com_motor(motor, codigo, avisar, verificar_continuacao=verificar)
        if resultado == ResultadoConsulta.CONFERIR_MANUALMENTE:
            raise FalhaOperacao(
                "inconclusivo",
                "A situação da encomenda não pôde ser confirmada após o novo login.",
                "Confira manualmente no SIAT. Resultado vazio não significa liberação.",
            )
        avisar("Consulta atualizada. Localizando a lupa na linha do rastreio informado.")
        motor.abrir_detalhes(codigo)
        avisar("Detalhes abertos. Lendo o motivo da retenção em Inf. Adicionais.")
        return motor.ler_retencao(codigo)

    def colar(self, texto):
        resultado = self.transporte.chamar("colar", valor=texto).get("resultado")
        antes_da_colagem = {
            "foco": "O WhatsApp não estava em primeiro plano com o campo de mensagem focado.",
            "campo_nao_identificado": "O campo de mensagem do WhatsApp não foi reconhecido.",
            "campo_nao_legivel": "Não foi possível conferir o campo de mensagem do WhatsApp.",
            "campo_ocupado": "O campo do WhatsApp já contém texto. A mensagem não foi substituída.",
            "tecla_pressionada": "Uma tecla de atalho estava pressionada no momento da colagem.",
            "clipboard_indisponivel": "A área de transferência do Windows estava ocupada.",
            "falha_pre_colagem": "A preparação da colagem falhou antes de inserir a mensagem.",
        }
        if resultado in antes_da_colagem:
            raise FalhaOperacao(
                "campo_sem_foco",
                antes_da_colagem[resultado],
                "A orientação do banco continua no painel. Tente novamente: durante os 8 segundos, "
                "abra a conversa e clique no campo vazio de mensagem. Solte as teclas de atalho.",
            )
        if resultado != "ok":
            raise FalhaOperacao(
                "colagem_incerta",
                "Não foi possível confirmar a colagem no WhatsApp.",
                "Confira o campo no WhatsApp antes de qualquer nova tentativa. "
                "A orientação do banco continua visível no painel.",
            )

    def retornar_painel(self):
        """Uma tentativa de retorno; falha de foco não invalida o resultado lido."""
        try:
            return self.transporte.chamar("retornar_painel").get("resultado") == "ok"
        except FalhaOperacao:
            return False

    def fechar(self):
        self.transporte.fechar()
