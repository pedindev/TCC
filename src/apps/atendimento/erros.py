"""Erros públicos, sem rastreio, dados da página ou exceções do navegador."""


class FalhaOperacao(Exception):
    def __init__(self, codigo, mensagem, acao):
        self.codigo = codigo
        self.mensagem = mensagem
        self.acao = acao
        super().__init__(mensagem)


class Cancelado(Exception):
    pass
