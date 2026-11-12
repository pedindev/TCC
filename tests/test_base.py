import os
import subprocess
import sys

from django.conf import settings
from django.test import Client, SimpleTestCase, override_settings

from apps.errors import IntegracaoIndisponivel
from apps.siat.service import consultar
from apps.whatsapp.service import enviar


class IntegrationBoundaryTests(SimpleTestCase):
    def test_consulta_nao_inventa_resultado(self):
        with self.assertRaises(IntegracaoIndisponivel):
            consultar("CASO-FICTICIO-01")

    def test_envio_nao_apresenta_sucesso_ficticio(self):
        with self.assertRaises(IntegracaoIndisponivel):
            enviar("DESTINATARIO-FICTICIO", "Mensagem ficticia")

    def test_erro_nao_expoe_argumentos(self):
        for operation, args in [
            (consultar, ("MARCADOR-PRIVADO",)),
            (enviar, ("MARCADOR-PRIVADO", "MARCADOR-PRIVADO")),
        ]:
            with self.subTest(operation=operation.__name__):
                try:
                    operation(*args)
                except IntegracaoIndisponivel as error:
                    self.assertNotIn("MARCADOR-PRIVADO", str(error))
                else:
                    self.fail("A integracao deveria permanecer indisponivel.")

    def test_modo_real_recusado_na_inicializacao(self):
        env = {**os.environ, "APP_MODE": "real"}
        result = subprocess.run(
            [sys.executable, "manage.py", "check"],
            cwd=settings.BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("APP_MODE=preparacao", result.stderr)


@override_settings(APP_MODE="preparacao")
class LocalAccessTests(SimpleTestCase):
    def test_inicio_informa_limites_e_nao_recebe_dados(self):
        response = self.client.get("/")
        self.assertContains(response, "Integrações reais indisponíveis")
        self.assertContains(response, 'id="rastreio"')
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_painel_abre_diretamente_sem_sessao_ou_banco(self):
        response = self.client.get("/painel/")
        self.assertContains(response, "Consultar encomenda")
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertNotIn("sessionid", response.cookies)

    def test_rotas_de_contas_removidas(self):
        for path in ("/entrar/", "/sair/", "/admin/", "/admin/login/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_posts_sem_csrf_sao_recusados(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post("/painel/", {}).status_code, 403)

    def test_acesso_remoto_recusado_mesmo_com_host_local(self):
        self.assertEqual(
            self.client.get("/", REMOTE_ADDR="192.0.2.1", HTTP_HOST="localhost").status_code,
            403,
        )

    def test_host_externo_recusado(self):
        self.assertEqual(self.client.get("/", HTTP_HOST="example.invalid").status_code, 400)
