from ipaddress import ip_address

from django.http import HttpResponseForbidden


class LocalOnlyMiddleware:
    """Recusa clientes remotos mesmo se o servidor for iniciado no endereco errado."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            local = ip_address(request.META.get("REMOTE_ADDR", "")).is_loopback
        except ValueError:
            local = False
        if not local:
            return HttpResponseForbidden("Este ambiente aceita apenas acesso local.")
        response = self.get_response(request)
        response["Cache-Control"] = "no-store"
        return response
