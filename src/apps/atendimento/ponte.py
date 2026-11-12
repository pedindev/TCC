"""Ponte local da extensão: somente estados, comandos em memória e respostas enumeradas."""

import secrets
import threading
import time

from apps.atendimento.erros import FalhaOperacao

ESTADOS = {
    "ausente": ("nao_aberto", "Aba não localizada neste navegador. Abra o site normalmente."),
    "duplicada": ("verificar", "Há mais de uma aba. Deixe apenas a aba que será usada."),
    "login": ("login", "Aba conectada. Faça login no próprio site."),
    "inicio": ("disponivel", "SIAT conectado. Página inicial reconhecida."),
    "consulta": ("disponivel", "SIAT conectado. Consulta disponível."),
    "pronto": ("disponivel", "WhatsApp conectado. Confira a conversa antes de colar."),
    "aberto": ("verificar", "Aba conectada. Confira o login e abra uma conversa."),
    "desconhecida": ("verificar", "Aba conectada. Confira a tela do sistema."),
    "erro": ("verificar", "Não foi possível verificar esta aba. Atualize o site."),
}
RESPOSTAS = {"ok", "vazio", "atualizado", "login", "demora", "falha", "sem_foco", "incerto"}


class PonteExtensao:
    def __init__(self):
        self.condicao = threading.Condition()
        self.instancia = None
        self.estados = {}
        self.ultima = 0
        self.pedido = None

    def sincronizar(self, dados):
        instancia = dados.get("instancia")
        if not isinstance(instancia, str) or not 8 <= len(instancia) <= 80:
            raise ValueError("Instância inválida.")
        estados = dados.get("estados")
        if not isinstance(estados, dict) or set(estados) != {"siat", "whatsapp"}:
            raise ValueError("Estados inválidos.")
        limpos = {}
        for nome, estado in estados.items():
            if not isinstance(estado, dict) or estado.get("estado") not in ESTADOS:
                raise ValueError("Estado inválido.")
            aba = estado.get("aba")
            if aba is not None and (type(aba) is not int or aba < 0):
                raise ValueError("Aba inválida.")
            limpos[nome] = {"estado": estado["estado"], "aba": aba}
        with self.condicao:
            if self.instancia != instancia and time.monotonic() - self.ultima < 12:
                raise ValueError("Já existe outro navegador conectado ao painel.")
            self.instancia, self.estados, self.ultima = instancia, limpos, time.monotonic()
            resposta = dados.get("resposta")
            if (
                isinstance(resposta, dict)
                and self.pedido
                and resposta.get("id") == self.pedido["id"]
            ):
                if resposta.get("resultado") not in RESPOSTAS:
                    raise ValueError("Resposta inválida.")
                self.pedido["resposta"] = resposta["resultado"]
                self.condicao.notify_all()
            if self.pedido and not self.pedido["emitido"] and time.time() < self.pedido["limite"]:
                self.pedido["emitido"] = True
                return {
                    chave: self.pedido[chave]
                    for chave in ("id", "sistema", "aba", "acao", "valor", "limite")
                }
        return None

    def status(self):
        with self.condicao:
            if time.monotonic() - self.ultima > 12 or not self.instancia:
                return {
                    nome: {
                        "estado": "indisponivel",
                        "texto": "Extensão MVP não conectada. "
                        "Instale-a neste navegador e atualize o painel.",
                    }
                    for nome in ("siat", "whatsapp")
                }
            return {
                nome: dict(zip(("estado", "texto"), ESTADOS[item["estado"]], strict=True))
                for nome, item in self.estados.items()
            }

    def referencia(self, sistema):
        with self.condicao:
            return self.instancia, self.estados.get(sistema, {}).get("aba")

    def estado_siat(self, referencia=None):
        with self.condicao:
            if time.monotonic() - self.ultima > 12:
                return "ausente"
            if referencia and referencia != self.referencia("siat"):
                return "ausente"
            return self.estados.get("siat", {}).get("estado", "ausente")

    def executar(self, sistema, acao, valor="", verificar=lambda: None, referencia=None):
        with self.condicao:
            aba = self.estados.get(sistema, {}).get("aba")
            if (
                aba is None
                or time.monotonic() - self.ultima > 12
                or self.pedido
                or referencia
                and referencia != self.referencia(sistema)
            ):
                raise FalhaOperacao(
                    "conexao",
                    "A aba não está disponível para esta ação.",
                    "Confira a extensão e mantenha uma única aba do sistema aberta.",
                )
            pedido = {
                "id": secrets.token_urlsafe(24),
                "sistema": sistema,
                "aba": aba,
                "acao": acao,
                "valor": valor,
                "limite": time.time() + 9,
                "emitido": False,
                "resposta": None,
            }
            self.pedido = pedido
        try:
            while time.time() < pedido["limite"]:
                try:
                    verificar()
                except Exception:
                    # Uma ação já emitida deve terminar antes de liberar outro atendimento.
                    with self.condicao:
                        if pedido["emitido"]:
                            self.condicao.wait_for(
                                lambda: pedido["resposta"] is not None,
                                timeout=max(0, pedido["limite"] - time.time()),
                            )
                    raise
                with self.condicao:
                    if pedido["resposta"] is not None:
                        return pedido["resposta"]
                    self.condicao.wait(timeout=0.1)
            raise FalhaOperacao(
                "colagem_incerta" if acao == "colar" else "demora",
                "A extensão não confirmou o término da ação.",
                "Confira a aba do sistema antes de tentar novamente.",
            )
        finally:
            with self.condicao:
                self.pedido = None
                pedido["valor"] = ""


ponte = PonteExtensao()
