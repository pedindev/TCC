from django.urls import path

from apps.atendimento import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("painel/", views.painel, name="painel"),
    path("api/estado/", views.estado, name="estado"),
    path("api/extensao/sincronizar/", views.sincronizar_extensao, name="extensao"),
    path("api/<str:acao>/", views.comando, name="comando"),
]
