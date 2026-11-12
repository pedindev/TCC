from apps.errors import IntegracaoIndisponivel


def enviar(destinatario: str, mensagem: str):
    """Envio não pertence ao MVP: o operador pressiona Enter manualmente."""
    raise IntegracaoIndisponivel(
        "O envio é manual. Use a colagem, confira a conversa e envie pelo navegador."
    )
