"""Um atendimento em memória e um worker por processo, inclusive entre abas."""

import copy
import math
import queue
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from django.db import close_old_connections
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from apps.atendimento.erros import Cancelado, FalhaOperacao
from apps.atendimento.simulacao import TEXTO_TESTE_COM
from apps.catalogo.service import preparar_orientacao
from apps.siat.consulta import FalhaPesquisaSiat, TempoPesquisaExcedido
from apps.siat.estado import LoginSiatNecessario, TelaConsultaIndisponivel
from apps.siat.navegacao import FalhaNavegacaoSiat
from apps.siat.resultado import MOTIVOS


def indisponiveis():
    return {
        nome: {"estado": "indisponivel", "texto": "Conexão não confirmada. Confira o navegador."}
        for nome in ("siat", "whatsapp")
    }


class FluxoOperador:
    def __init__(
        self,
        fabrica,
        *,
        modo="preparacao",
        catalogo=preparar_orientacao,
        contagem=8,
        prazo=360,
        retencao=900,
    ):
        self.fabrica, self.modo, self.catalogo = fabrica, modo, catalogo
        self.contagem, self.prazo, self.retencao = contagem, prazo, retencao
        self.lock = threading.RLock()
        self.fila = queue.Queue(maxsize=1)
        self.parar = threading.Event()
        self.cancelar = threading.Event()
        self.ocupado = False
        self.sistemas = indisponiveis()
        self.ultimo_status = 0
        self.ultima_atividade = time.monotonic()
        self.estado = self._limpo()
        self.thread = threading.Thread(target=self._executar, daemon=True, name="mvp-navegador")
        self.thread.start()

    def _limpo(self):
        return {
            "atendimento": uuid.uuid4().hex,
            "token": uuid.uuid4().hex,
            "fase": "inicial",
            "rastreio": "",
            "situacao": "",
            "motivo": "",
            "mensagem": "",
            "mensagens": [],
            "mensagem_indice": 0,
            "colagens_tentadas": [],
            "versao": "",
            "aviso_catalogo": "",
            "pode_colar": False,
            "colagem_tentada": False,
            "segundos": 0,
            "erro": "",
            "aviso": "Cole o código de rastreio para iniciar.",
            "acao": "",
        }

    def snapshot(self):
        with self.lock:
            self._expirar()
            self.ultima_atividade = time.monotonic()
            return copy.deepcopy(
                {
                    **self.estado,
                    "ocupado": self.ocupado,
                    "sistemas": self.sistemas,
                    "modo": self.modo,
                }
            )

    def _expirar(self):
        if time.monotonic() - self.ultima_atividade > self.retencao:
            self.cancelar.set()
            self.estado = self._limpo()
            self.ultima_atividade = time.monotonic()
            self.estado["aviso"] = (
                "Atendimento encerrado por inatividade. Inicie uma nova consulta."
            )

    def _conferir(self, atendimento, token):
        if atendimento != self.estado["atendimento"] or token != self.estado["token"]:
            raise FalhaOperacao(
                "desatualizado",
                "Esta ação já foi usada ou pertence a outro atendimento.",
                "Confira o estado atual do painel antes de continuar.",
            )

    def consultar(self, atendimento, token, codigo):
        if isinstance(codigo, str):
            codigo = "".join(
                c for c in codigo if not c.isspace() and c not in "\u200b\ufeff"
            ).upper()
        if (
            not isinstance(codigo, str)
            or not 1 <= len(codigo) <= 64
            or any(ord(c) < 32 for c in codigo)
        ):
            raise FalhaOperacao(
                "codigo_invalido",
                "Informe um código de rastreio válido, com até 64 caracteres.",
                "Confira o código recebido e cole novamente.",
            )
        with self.lock:
            self._conferir(atendimento, token)
            if self.ocupado or self.estado["fase"] != "inicial":
                raise FalhaOperacao(
                    "ocupado",
                    "Já existe um atendimento em andamento.",
                    "Aguarde ou clique em Novo atendimento.",
                )
            if self.modo == "preparacao":
                raise FalhaOperacao(
                    "conexao",
                    "O navegador de atendimento não está conectado.",
                    "Inicie a simulação ou configure a conexão do navegador.",
                )
            self.cancelar.clear()
            self.ocupado = True
            self.estado.update(
                token=uuid.uuid4().hex,
                fase="consultando",
                rastreio=codigo,
                aviso="Consultando no SIAT. Aguarde.",
                acao="",
                erro="",
            )
            self.ultima_atividade = time.monotonic()
            self.fila.put_nowait(("consultar", atendimento, codigo))

    def colar(self, atendimento, token):
        with self.lock:
            self._conferir(atendimento, token)
            if self.ocupado or not self.estado["pode_colar"] or self.estado["colagem_tentada"]:
                raise FalhaOperacao(
                    "colagem_bloqueada",
                    "A colagem não está disponível neste momento.",
                    "Confira o resultado e os avisos do painel.",
                )
            if self.sistemas["whatsapp"]["estado"] != "disponivel":
                raise FalhaOperacao(
                    "whatsapp_indisponivel",
                    "O WhatsApp está indisponível.",
                    "Abra a conversa no navegador. A orientação permanece no painel.",
                )
            self.cancelar.clear()
            self.ocupado = True
            self.estado.update(
                token=uuid.uuid4().hex,
                fase="contagem",
                erro="",
                acao="",
                segundos=self.contagem,
                aviso="Abra a conversa certa e clique no campo de mensagem.",
            )
            self.ultima_atividade = time.monotonic()
            self.fila.put_nowait(("colar", atendimento, self.estado["mensagem"]))

    def selecionar_mensagem(self, atendimento, token, indice):
        with self.lock:
            self._conferir(atendimento, token)
            if self.ocupado:
                raise FalhaOperacao(
                    "ocupado", "Aguarde a operação atual.", "Troque a mensagem após a conclusão."
                )
            if type(indice) is not int or not 0 <= indice < len(self.estado["mensagens"]):
                raise FalhaOperacao(
                    "mensagem_invalida",
                    "Mensagem não disponível.",
                    "Confira as opções do atendimento.",
                )
            opcao = self.estado["mensagens"][indice]
            self.estado.update(
                token=uuid.uuid4().hex,
                fase="pronto",
                mensagem_indice=indice,
                mensagem=opcao["texto"],
                versao=opcao["versao"],
                aviso_catalogo=opcao["aviso"],
                pode_colar=opcao["pode_colar"],
                colagem_tentada=indice in self.estado["colagens_tentadas"],
                aviso=f"Mensagem {indice + 1} selecionada. Confira o texto antes de colar.",
                acao="",
                erro="",
                segundos=0,
            )
            self.ultima_atividade = time.monotonic()

    def novo(self, atendimento, token):
        with self.lock:
            self._conferir(atendimento, token)
            self.cancelar.set()
            self.estado = self._limpo()
            if self.ocupado:
                self.estado["aviso"] = (
                    "Encerrando a operação anterior. Aguarde para consultar novamente."
                )
            self.ultima_atividade = time.monotonic()

    def cancelar_colagem(self, atendimento, token):
        with self.lock:
            self._conferir(atendimento, token)
            if self.estado["fase"] != "contagem":
                raise FalhaOperacao(
                    "colagem_iniciada",
                    "A contagem já terminou.",
                    "Confira o campo de mensagem no WhatsApp.",
                )
            self.cancelar.set()
            self.estado.update(
                token=uuid.uuid4().hex,
                fase="pronto",
                segundos=0,
                aviso="Colagem cancelada. A orientação foi mantida.",
            )

    def _atualizar(self, atendimento, **campos):
        with self.lock:
            if self.estado["atendimento"] == atendimento:
                self.estado.update(campos)

    def _observar(self, navegador):
        if time.monotonic() - self.ultimo_status < 1:
            return
        try:
            sistemas = navegador.status()
        except Exception:
            sistemas = indisponiveis()
        with self.lock:
            self.sistemas = sistemas
        self.ultimo_status = time.monotonic()

    def _executar(self):
        navegador = self.fabrica()
        catalogo_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mvp-catalogo")
        try:
            while not self.parar.is_set():
                self._observar(navegador)
                with self.lock:
                    self._expirar()
                try:
                    operacao, atendimento, valor = self.fila.get(timeout=0.2)
                except queue.Empty:
                    continue
                limite = time.monotonic() + self.prazo

                def verificar(atendimento=atendimento, limite=limite):
                    with self.lock:
                        self._expirar()
                        if (
                            self.parar.is_set()
                            or self.cancelar.is_set()
                            or (atendimento != self.estado["atendimento"])
                        ):
                            raise Cancelado()
                    if time.monotonic() > limite:
                        raise FalhaOperacao(
                            "demora",
                            "A consulta excedeu o tempo de espera.",
                            "Confira o navegador e inicie um novo atendimento.",
                        )
                    self._observar(navegador)

                def avisar(texto, atendimento=atendimento, verificar=verificar):
                    verificar()
                    self._atualizar(
                        atendimento,
                        aviso=texto,
                        fase=(
                            "aguardando_login" if texto.startswith("Faça login") else "consultando"
                        ),
                    )

                try:
                    verificar()
                    if operacao == "consultar":
                        resultado = navegador.consultar(valor, avisar, verificar)
                        verificar()
                        try:
                            resultado.validar()
                        except FalhaOperacao as erro:
                            if erro.codigo == "motivo_desconhecido":
                                self._atualizar(
                                    atendimento, situacao="retida", motivo="Não reconhecido"
                                )
                            raise
                        if resultado.confirmado:
                            self._atualizar(
                                atendimento,
                                situacao=resultado.situacao,
                                motivo=(
                                    resultado.descricao_retencao
                                    or MOTIVOS.get(resultado.motivo, "Não reconhecido")
                                )
                                if resultado.situacao == "retida"
                                else "Não se aplica",
                            )
                        try:
                            if resultado.situacao == "retida" and resultado.motivo not in MOTIVOS:
                                raise FalhaOperacao("orientacao_indisponivel", "", "")
                            orientacao = catalogo_executor.submit(
                                self._carregar_orientacao, resultado, valor
                            ).result(timeout=5)
                        except FalhaOperacao as erro:
                            if (
                                erro.codigo != "orientacao_indisponivel"
                                or not resultado.descricao_retencao
                            ):
                                raise
                            verificar()
                            self._atualizar(
                                atendimento,
                                fase="pronto",
                                mensagem="",
                                versao="",
                                pode_colar=False,
                                aviso_catalogo=(
                                    "Não há uma orientação disponível para esta retenção."
                                ),
                                aviso="Consulta concluída. Confira a retenção informada pelo SIAT.",
                                acao="Prossiga com a orientação manual da equipe do posto.",
                            )
                            continue
                        verificar()
                        self._atualizar(
                            atendimento,
                            fase="pronto",
                            mensagem=orientacao["texto"],
                            mensagens=orientacao.get(
                                "mensagens", [{**orientacao, "titulo": "Orientação"}]
                            ),
                            mensagem_indice=0,
                            versao=orientacao["versao"],
                            aviso_catalogo=orientacao["aviso"],
                            pode_colar=orientacao["pode_colar"],
                            aviso="Consulta concluída. Confira a orientação completa.",
                            acao=""
                            if orientacao["pode_colar"]
                            else "Confira o aviso do catálogo antes de usar a orientação.",
                        )
                    else:
                        fim = time.monotonic() + self.contagem
                        while time.monotonic() < fim:
                            verificar()
                            self._atualizar(atendimento, segundos=math.ceil(fim - time.monotonic()))
                            self.cancelar.wait(0.1)
                        verificar()
                        # Marca a tentativa antes do efeito externo. Novo atendimento não
                        # pode intercalar a invalidação com a colagem já iniciada.
                        with self.lock:
                            verificar()
                            self._atualizar(
                                atendimento,
                                fase="colando",
                                segundos=0,
                                colagem_tentada=True,
                                colagens_tentadas=[
                                    *self.estado["colagens_tentadas"],
                                    self.estado["mensagem_indice"],
                                ],
                            )
                            navegador.colar(valor)
                        self._atualizar(
                            atendimento,
                            fase="colado",
                            aviso="Texto colado. O envio é manual.",
                            acao="Confira o destinatário e a mensagem no WhatsApp. "
                            "Pressione Enter para enviar.",
                        )
                except Cancelado:
                    pass
                except Exception as erro:
                    falha = self._falha_publica(erro)
                    self._atualizar(
                        atendimento,
                        fase="erro",
                        erro=falha.codigo,
                        aviso=falha.mensagem,
                        acao=falha.acao,
                        segundos=0,
                    )
                    if falha.codigo in {"campo_sem_foco", "whatsapp_indisponivel"}:
                        with self.lock:
                            self._atualizar(
                                atendimento,
                                colagem_tentada=False,
                                colagens_tentadas=[
                                    i
                                    for i in self.estado["colagens_tentadas"]
                                    if i != self.estado["mensagem_indice"]
                                ],
                            )
                finally:
                    valor = None
                    with self.lock:
                        devolver_foco = (
                            operacao == "consultar"
                            and self.estado["atendimento"] == atendimento
                            and self.estado["fase"] == "pronto"
                            and not self.cancelar.is_set()
                        )
                    retornar = getattr(navegador, "retornar_painel", None)
                    if devolver_foco and retornar:
                        # Resultado já publicado: retornar ao painel, inclusive sem orientação.
                        # Uma falha aqui nunca apaga a retenção nem repete a consulta.
                        try:
                            voltou = retornar()
                        except Exception:
                            voltou = False
                        if not voltou:
                            self._atualizar(
                                atendimento,
                                acao="Consulta concluída. Volte à aba Painel • MVP para conferir.",
                            )
                    with self.lock:
                        self.ocupado = False
                        if self.estado["fase"] == "inicial":
                            self.estado["aviso"] = "Cole o código de rastreio para iniciar."
                    self.fila.task_done()
        finally:
            catalogo_executor.shutdown(wait=False, cancel_futures=True)
            navegador.fechar()

    def _carregar_orientacao(self, resultado, codigo):
        if self.modo == "simulacao" and codigo == "TESTE-COM":
            return {"texto": TEXTO_TESTE_COM, "versao": "", "aviso": "", "pode_colar": True}
        # Django ORM não deve executar na thread que mantém o event loop do Playwright.
        close_old_connections()
        try:
            return self.catalogo(resultado, simulado=self.modo == "simulacao")
        finally:
            close_old_connections()

    @staticmethod
    def _falha_publica(erro):
        if isinstance(erro, FalhaOperacao):
            return erro
        if isinstance(erro, LoginSiatNecessario):
            return FalhaOperacao(
                "sessao_expirada",
                "O login no SIAT não foi confirmado.",
                "Faça login no navegador e inicie um novo atendimento.",
            )
        if isinstance(erro, (PlaywrightTimeout, TimeoutError, TempoPesquisaExcedido)):
            return FalhaOperacao(
                "demora",
                "O sistema demorou mais que o esperado.",
                "Confira o navegador e inicie um novo atendimento.",
            )
        if isinstance(erro, (FalhaPesquisaSiat, TelaConsultaIndisponivel, FalhaNavegacaoSiat)):
            return FalhaOperacao(
                "falha_consulta",
                "Não foi possível concluir a consulta no SIAT.",
                "Confira a conexão, o login e a tela de consulta. Depois tente novamente.",
            )
        if isinstance(erro, PlaywrightError):
            return FalhaOperacao(
                "conexao",
                "A conexão com o navegador foi interrompida.",
                "Reabra o navegador de atendimento e confira o login.",
            )
        return FalhaOperacao(
            "falha_interna",
            "Não foi possível concluir esta operação.",
            "Inicie um novo atendimento. Se persistir, procure o suporte do MVP.",
        )

    def fechar(self):
        self.parar.set()
        self.cancelar.set()
        self.thread.join(timeout=10)
