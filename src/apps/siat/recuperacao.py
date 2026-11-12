"""Recuperação do possível falso resultado vazio informado pelo operador."""

from collections.abc import Callable
from enum import Enum
from time import monotonic

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from apps.siat.consulta import pesquisar_rastreio
from apps.siat.estado import LoginSiatNecessario, TelaConsultaIndisponivel
from apps.siat.navegacao import abrir_consulta_notificacao
from apps.siat.sessao import (
    EstadoSessao,
    aguardar_login_manual,
    estado_sessao,
    sair_do_siat,
)


class ResultadoConsulta(Enum):
    PROSSEGUIR_LEITURA = "resultado_atualizado_leitura_pendente"
    CONFERIR_MANUALMENTE = "sem_informacoes_apos_novo_login"


def consultar_com_recuperacao(
    page: Page,
    codigo: str,
    avisar: Callable[[str], None],
    *,
    timeout_ms: int = 5000,
    timeout_login_ms: int = 300000,
    verificar_continuacao: Callable[[], None] = lambda: None,
) -> ResultadoConsulta:
    """Recebe uma Page já conectada; código só em memória, sem banco ou logs.

    Callback avisar deve publicar a orientação na interface do operador.
    No máximo uma recuperação por chamada; não abre notificações nem infere
    liberação ou inexistência de mercadoria. Login inicial não consome a recuperação.
    """
    return recuperar_com_motor(
        MotorPlaywright(page, timeout_ms),
        codigo,
        avisar,
        timeout_ms=timeout_ms,
        timeout_login_ms=timeout_login_ms,
        verificar_continuacao=verificar_continuacao,
    )


class MotorPlaywright:
    def __init__(self, page, timeout_ms):
        self.page, self.timeout_ms = page, timeout_ms

    def estado(self):
        return estado_sessao(self.page)

    def abrir(self):
        abrir_consulta_notificacao(self.page, timeout_ms=self.timeout_ms)

    def pesquisar(self, codigo):
        pesquisar_rastreio(self.page, codigo, timeout_ms=self.timeout_ms, aguardar_atualizacao=True)

    def vazia(self):
        tabela = self.page.locator('[id="frmConsultar:dTableNotificacao"]')
        tabela.wait_for(state="visible", timeout=self.timeout_ms)
        return tabela.get_by_text("Nenhuma Notificação encontrada!", exact=True).is_visible()

    def sair(self):
        sair_do_siat(self.page, timeout_ms=self.timeout_ms)

    def aguardar_login(self, avisar, timeout_ms, verificar):
        aguardar_login_manual(
            self.page, avisar, timeout_ms=timeout_ms, verificar_continuacao=verificar
        )


def recuperar_com_motor(
    motor,
    codigo,
    avisar,
    *,
    timeout_ms=5000,
    timeout_login_ms=300000,
    verificar_continuacao=lambda: None,
):
    """Uma política de recuperação compartilhada pelos adaptadores de navegador."""

    def esperar_login():
        if hasattr(motor, "aguardar_login"):
            return motor.aguardar_login(avisar, timeout_login_ms, verificar_continuacao)
        avisar(
            "Faça login novamente no SIAT pelo navegador. A consulta será repetida após o login."
        )
        limite = monotonic() + timeout_login_ms / 1000
        while monotonic() < limite:
            verificar_continuacao()
            if motor.estado() in (EstadoSessao.INICIO, EstadoSessao.CONSULTA):
                return
            motor.pausar()
        raise LoginSiatNecessario(
            "O login não foi confirmado no prazo. Inicie a consulta novamente."
        )

    if not 0 < timeout_ms <= 30000 or not 0 < timeout_login_ms <= 1800000:
        raise ValueError("Prazos de consulta ou login inválidos.")
    if (
        not isinstance(codigo, str)
        or not codigo.strip()
        or any(c.isspace() for c in codigo.strip())
    ):
        raise ValueError("Informe um código de rastreio sem espaços.")
    recuperou = False
    verificar_continuacao()
    if motor.estado() == EstadoSessao.LOGIN:
        esperar_login()
    while True:
        verificar_continuacao()
        try:
            estado = motor.estado()
            if estado == EstadoSessao.LOGIN:
                raise LoginSiatNecessario("O SIAT solicitou novo login.")
            if estado == EstadoSessao.INICIO:
                motor.abrir()
            elif estado != EstadoSessao.CONSULTA:
                raise TelaConsultaIndisponivel(
                    "A tela do SIAT não foi reconhecida. Confira o navegador."
                )
            motor.pesquisar(codigo)
            verificar_continuacao()
            avisar("Consulta realizada. Conferindo a resposta do SIAT.")
            vazio = motor.vazia()
            if motor.estado() == EstadoSessao.LOGIN:
                raise LoginSiatNecessario("O SIAT solicitou novo login.")
            if not vazio:
                # Ausência da mensagem não comprova que há uma carta: leitura é a próxima etapa.
                return ResultadoConsulta.PROSSEGUIR_LEITURA
            if recuperou:
                avisar(
                    "O SIAT continua sem mostrar informações após o novo login. "
                    "Confira a consulta manualmente; isso não confirma ausência de notificação."
                )
                return ResultadoConsulta.CONFERIR_MANUALMENTE
            avisar(
                "O SIAT não mostrou informações. Vou sair para renovar a sessão e tentar novamente."
            )
            motor.sair()
        except LoginSiatNecessario:
            if recuperou:
                raise LoginSiatNecessario(
                    "O SIAT voltou a pedir login após a tentativa de recuperação. "
                    "Confira o navegador."
                ) from None
        except PlaywrightError:
            if motor.estado() != EstadoSessao.LOGIN:
                raise TelaConsultaIndisponivel(
                    "Não foi possível confirmar a resposta do SIAT."
                ) from None
            if recuperou:
                raise LoginSiatNecessario(
                    "O SIAT voltou a pedir login. Confira o navegador."
                ) from None
        recuperou = True
        esperar_login()
