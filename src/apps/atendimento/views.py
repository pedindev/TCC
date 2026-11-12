import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_POST

from apps.atendimento.erros import FalhaOperacao
from apps.atendimento.ponte import ponte
from apps.atendimento.runtime import obter_fluxo


@require_POST
@sensitive_post_parameters()
def sincronizar_extensao(request):
    if settings.APP_MODE != "navegador":
        return JsonResponse({"comando": None})
    try:
        if len(request.body) > 4096:
            raise ValueError()
        dados = json.loads(request.body)
        if not isinstance(dados, dict):
            raise ValueError()
        return JsonResponse({"comando": ponte.sincronizar(dados)})
    except (ValueError, UnicodeError, TypeError):
        return JsonResponse(
            {"erro": "Conexão inválida ou outro navegador já conectado."}, status=400
        )


@require_GET
@ensure_csrf_cookie
def inicio(request):
    return render(request, "atendimento/painel.html", {"modo": settings.APP_MODE})


@require_GET
@ensure_csrf_cookie
def painel(request):
    return inicio(request)


@require_GET
def estado(request):
    return JsonResponse(obter_fluxo().snapshot())


@require_POST
@sensitive_post_parameters()
def comando(request, acao):
    try:
        dados = json.loads(request.body)
        if not isinstance(dados, dict):
            raise ValueError()
        atendimento, token = dados.get("atendimento"), dados.get("token")
        if not isinstance(atendimento, str) or not isinstance(token, str):
            raise ValueError()
    except (ValueError, UnicodeError):
        return JsonResponse(
            {"mensagem": "Pedido inválido.", "acao": "Atualize o painel."}, status=400
        )
    fluxo = obter_fluxo()
    try:
        if acao == "consultar":
            fluxo.consultar(atendimento, token, dados.get("codigo"))
        elif acao == "colar":
            fluxo.colar(atendimento, token)
        elif acao == "selecionar_mensagem":
            fluxo.selecionar_mensagem(atendimento, token, dados.get("indice"))
        elif acao == "novo":
            fluxo.novo(atendimento, token)
        elif acao == "cancelar":
            fluxo.cancelar_colagem(atendimento, token)
        else:
            return JsonResponse({"mensagem": "Ação não reconhecida."}, status=404)
    except FalhaOperacao as erro:
        return JsonResponse(
            {"mensagem": erro.mensagem, "acao": erro.acao, "codigo": erro.codigo}, status=409
        )
    return JsonResponse(fluxo.snapshot(), status=202)
