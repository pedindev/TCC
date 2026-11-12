"""Adaptador das abas do navegador comum, sem CDP nem abertura de janelas."""

import time

from apps.atendimento.erros import FalhaOperacao
from apps.atendimento.ponte import ponte
from apps.siat.recuperacao import ResultadoConsulta, recuperar_com_motor
from apps.siat.resultado import ler_resultado_real
from apps.siat.sessao import EstadoSessao


class MotorExtensao:
    def __init__(self, verificar):
        self.verificar = verificar
        self.resultado = None
        self.referencia = ponte.referencia("siat")

    def estado(self):
        return {
            "login": EstadoSessao.LOGIN,
            "inicio": EstadoSessao.INICIO,
            "consulta": EstadoSessao.CONSULTA,
        }.get(ponte.estado_siat(self.referencia), EstadoSessao.DESCONHECIDA)

    def acionar(self, acao, valor=""):
        resultado = ponte.executar("siat", acao, valor, self.verificar, self.referencia)
        if resultado == "login":
            from apps.siat.estado import LoginSiatNecessario

            raise LoginSiatNecessario("Faça login no SIAT.")
        if resultado in {"falha", "demora"}:
            raise FalhaOperacao(
                resultado,
                "Não foi possível concluir a ação no SIAT.",
                "Confira a aba do SIAT e tente novamente.",
            )
        return resultado

    def abrir(self):
        self.acionar("abrir_consulta")

    def pesquisar(self, codigo):
        self.resultado = self.acionar("consultar", codigo)

    def vazia(self):
        return self.resultado == "vazio"

    def sair(self):
        self.acionar("sair")

    def pausar(self):
        time.sleep(0.2)


class NavegadorExtensao:
    def status(self):
        return ponte.status()

    def consultar(self, codigo, avisar, verificar):
        resultado = recuperar_com_motor(
            MotorExtensao(verificar), codigo, avisar, verificar_continuacao=verificar
        )
        if resultado == ResultadoConsulta.CONFERIR_MANUALMENTE:
            raise FalhaOperacao(
                "inconclusivo",
                "A situação da encomenda não pôde ser confirmada após o novo login.",
                "Confira manualmente no SIAT; resultado vazio não significa liberação.",
            )
        return ler_resultado_real(None, codigo)

    def colar(self, texto):
        resultado = ponte.executar("whatsapp", "colar", texto)
        if resultado != "ok":
            raise FalhaOperacao(
                "campo_sem_foco" if resultado == "sem_foco" else "colagem_incerta",
                "Não foi possível confirmar a colagem no WhatsApp.",
                "Confira a conversa e o campo de mensagem antes de repetir a ação.",
            )

    def fechar(self):
        pass
