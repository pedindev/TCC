"""Seleciona versões atuais; nunca promove rascunhos nem usa versões antigas como fallback."""

from django.utils import timezone

from apps.atendimento.erros import FalhaOperacao
from apps.catalogo.models import GuiaPortal, Orientacao

CODIGOS = {
    "comercializacao": ("COM-01", "SAC-PEDIDO-COM"),
    "simei": ("SIM-01", "SAC-PEDIDO-SIM"),
    "difal": ("DIF-01", "SAC-PEDIDO-DIF"),
    "irregularidades_fiscais": ("IRF-01", "SAC-PEDIDO-IRF"),
    "sem_nota_fiscal": ("SNF-01", None),
}


def preparar_orientacao(resultado, *, simulado=False):
    resultado.validar()
    if resultado.situacao != "retida" or resultado.motivo not in CODIGOS:
        raise FalhaOperacao(
            "orientacao_indisponivel",
            "A situação foi confirmada, mas não há orientação cadastrada.",
            "Oriente manualmente conforme o procedimento do posto.",
        )
    codigo, guia_codigo = CODIGOS[resultado.motivo]
    item = Orientacao.objects.filter(codigo=codigo).order_by("-versao").first()
    guia = (
        GuiaPortal.objects.filter(codigo=guia_codigo).order_by("-versao").first()
        if guia_codigo
        else None
    )
    if not item or not item.texto.strip() or (guia_codigo and (not guia or not guia.texto.strip())):
        raise FalhaOperacao(
            "orientacao_indisponivel",
            "A orientação correspondente não está disponível.",
            "Solicite a revisão do catálogo e mantenha o atendimento manual.",
        )
    hoje = timezone.localdate()
    revisada = item.estado == "revisado" and (not guia or guia.estado == "revisado")
    vigente = (not item.vigencia_inicio or item.vigencia_inicio <= hoje) and (
        not item.vigencia_fim or item.vigencia_fim >= hoje
    )
    texto = item.texto + ("\n\n" + guia.texto if guia else "")
    if simulado:
        texto = "[SIMULAÇÃO — DADOS FICTÍCIOS; NÃO ENVIAR A CONTRIBUINTES]\n\n" + texto
    principal = {
        "texto": texto,
        "versao": f"{item.codigo} v{item.versao}"
        + (f" · {guia.codigo} v{guia.versao}" if guia else ""),
        # Colagem não é envio nem aprovação editorial. O operador confere o texto
        # no painel e o destinatário no WhatsApp, e envia manualmente.
        "pode_colar": simulado or vigente,
        "aviso": ""
        if revisada and vigente
        else "Colagem indisponível: a orientação está fora do período de vigência."
        if not vigente
        else "Texto ainda marcado como rascunho no catálogo. Confira a orientação antes de "
        "colar e enviar manualmente. A colagem não altera o estado de revisão.",
    }
    opcoes = [{**principal, "titulo": "Orientação"}]
    if resultado.motivo == "sem_nota_fiscal":
        opcoes[0]["titulo"] = "Enviar a nota do fornecedor"
        avulsa = GuiaPortal.objects.filter(codigo="SAC-PEDIDO-NFA").order_by("-versao").first()
        disponivel = bool(avulsa and avulsa.texto.strip())
        texto_avulsa = avulsa.texto if disponivel else ""
        if simulado and disponivel:
            texto_avulsa = (
                "[SIMULAÇÃO — DADOS FICTÍCIOS; NÃO ENVIAR A CONTRIBUINTES]\n\n" + texto_avulsa
            )
        opcoes.append(
            {
                "titulo": "Solicitar nota fiscal avulsa",
                "texto": texto_avulsa,
                "versao": f"{avulsa.codigo} v{avulsa.versao}" if avulsa else "",
                "pode_colar": disponivel and (simulado or vigente),
                "aviso": "Orientação de nota fiscal avulsa indisponível no catálogo."
                if not disponivel
                else principal["aviso"]
                if not vigente
                else "Texto ainda em rascunho. Confira antes de colar e enviar manualmente."
                if avulsa.estado != "revisado"
                else "",
            }
        )
    return {**principal, "mensagens": opcoes}
