import atexit
import os
import threading

from django.conf import settings

from apps.atendimento.desktop import NavegadorDesktop
from apps.atendimento.fluxo import FluxoOperador
from apps.atendimento.navegador import Navegador

_lock = threading.Lock()
_fluxo = None


def obter_fluxo():
    global _fluxo
    with _lock:
        if _fluxo is None:
            os.environ.setdefault(
                "PLAYWRIGHT_BROWSERS_PATH", str(settings.BASE_DIR / ".local/browsers")
            )
            _fluxo = FluxoOperador(
                lambda: (
                    NavegadorDesktop()
                    if settings.APP_MODE == "navegador"
                    else Navegador(
                        modo=settings.APP_MODE,
                        endpoint=settings.NAVEGADOR_CDP,
                        campo_whatsapp=settings.WHATSAPP_CAMPO_MENSAGEM,
                    )
                ),
                modo=settings.APP_MODE,
            )
            atexit.register(_fluxo.fechar)
        return _fluxo
