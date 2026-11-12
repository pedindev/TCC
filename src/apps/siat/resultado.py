"""Contrato da leitura confirmada. Não deduz situação pela existência de uma linha."""

import re
import unicodedata
from dataclasses import dataclass

from apps.atendimento.erros import FalhaOperacao

MOTIVOS = {
    "comercializacao": "Comercialização",
    "simei": "SIMEI",
    "sem_nota_fiscal": "Sem nota fiscal",
    "difal": "E-commerce / DIFAL",
    "irregularidades_fiscais": "Irregularidades fiscais",
}

# Somente nomes explícitos: "ICMS", por exemplo, não identifica sozinho uma categoria.
PADROES = {
    "comercializacao": r"\bcomercializacao\b",
    "simei": r"\bsimei\b",
    "sem_nota_fiscal": (
        r"\b(?:(?:sem|ausencia de|desacompanhad[ao]s? de) notas? fisca(?:l|is)"
        r"|mercadorias? sem notas?)\b"
    ),
    "difal": r"\b(?:difal|e[\s-]?commerce|comercio eletronico)\b",
    "irregularidades_fiscais": r"\b(?:irregularidades? fisca(?:l|is)|situacao fiscal irregular)\b",
}


def resultado_da_retencao(descricao):
    """Preserva o campo; normalização serve apenas à seleção do catálogo."""
    if not isinstance(descricao, str) or not descricao.strip() or len(descricao) > 250:
        raise FalhaOperacao(
            "inconclusivo",
            "Não foi possível ler o motivo da retenção.",
            "Confira o campo Inf. Adicionais na janela de detalhes do SIAT.",
        )
    normalizado = "".join(
        c
        for c in unicodedata.normalize("NFKD", descricao.casefold())
        if not unicodedata.combining(c)
    )
    normalizado = re.sub(r"\s+", " ", normalizado)
    categorias = []
    negacao = False
    for chave, padrao in PADROES.items():
        for trecho in re.finditer(padrao, normalizado):
            if chave not in categorias:
                categorias.append(chave)
            # "Imposto não recolhido" não nega SIMEI; "não é SIMEI" nega a categoria.
            antes = normalizado[: trecho.start()]
            depois = normalizado[trecho.end() :]
            negacao = negacao or bool(
                re.search(
                    r"\b(?:nao(?: e| ha| se trata de| corresponde a| se enquadra em)?|"
                    r"sem|exceto|descartar|desconsiderar)\s*$",
                    antes,
                )
                or re.search(
                    r"^\s*(?:[-:]\s*)?(?:descartad[ao]|nao se aplica|nao aplicavel)\b",
                    depois,
                )
            )
    motivo = categorias[0] if len(categorias) == 1 and not negacao else ""
    return Resultado("retida", motivo, True, descricao)


@dataclass(frozen=True)
class Resultado:
    situacao: str
    motivo: str = ""
    confirmado: bool = False
    descricao_retencao: str = ""

    def validar(self):
        if not self.confirmado or self.situacao not in {"retida", "liberada"}:
            raise FalhaOperacao(
                "inconclusivo",
                "A situação da encomenda não pôde ser confirmada.",
                "Confira a consulta no SIAT antes de orientar o contribuinte.",
            )
        if self.descricao_retencao and (
            not isinstance(self.descricao_retencao, str)
            or not self.descricao_retencao.strip()
            or len(self.descricao_retencao) > 250
        ):
            raise FalhaOperacao(
                "inconclusivo", "Descrição da retenção inválida.", "Confira o SIAT."
            )
        if self.situacao == "retida" and self.motivo not in MOTIVOS and not self.descricao_retencao:
            raise FalhaOperacao(
                "motivo_desconhecido",
                "A retenção foi confirmada, mas o motivo não foi reconhecido.",
                "Confira o motivo no SIAT e encaminhe o caso à equipe responsável.",
            )
        if self.situacao == "liberada" and (self.motivo or self.descricao_retencao):
            raise FalhaOperacao(
                "inconclusivo",
                "O resultado apresenta informações incompatíveis.",
                "Confira a situação e o motivo no SIAT.",
            )


def ler_resultado_real(page, codigo):
    """Não inventar seletores de detalhe nem vínculo com a encomenda pesquisada."""
    raise FalhaOperacao(
        "leitura_pendente",
        "A consulta terminou, mas a situação ainda não pôde ser confirmada.",
        "Confira os detalhes no SIAT. A leitura da situação e do motivo ainda precisa ser mapeada.",
    )
