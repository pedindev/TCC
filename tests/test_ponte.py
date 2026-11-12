import threading
import time
from unittest.mock import patch

from django.test import Client, SimpleTestCase, override_settings

from apps.atendimento.erros import FalhaOperacao
from apps.atendimento.ponte import PonteExtensao
from apps.siat.recuperacao import ResultadoConsulta, recuperar_com_motor
from apps.siat.sessao import EstadoSessao


def estados(siat="login", whatsapp="pronto"):
    return {
        "instancia": "instancia-teste",
        "estados": {
            "siat": {"estado": siat, "aba": 10 if siat != "ausente" else None},
            "whatsapp": {"estado": whatsapp, "aba": 20 if whatsapp != "ausente" else None},
        },
    }


class PonteTests(SimpleTestCase):
    def test_nao_troca_aba_no_meio_da_consulta(self):
        ponte = PonteExtensao()
        ponte.sincronizar(estados("consulta"))
        referencia = ponte.referencia("siat")
        novos = estados("consulta")
        novos["estados"]["siat"]["aba"] = 30
        ponte.sincronizar(novos)
        self.assertEqual(ponte.estado_siat(referencia), "ausente")
        with self.assertRaises(FalhaOperacao):
            ponte.executar("siat", "consultar", "TESTE", referencia=referencia)

    def test_estados_independentes_e_expiracao(self):
        ponte = PonteExtensao()
        ponte.sincronizar(estados("ausente"))
        self.assertEqual(ponte.status()["siat"]["estado"], "nao_aberto")
        self.assertEqual(ponte.status()["whatsapp"]["estado"], "disponivel")
        ponte.sincronizar(estados("consulta", "ausente"))
        self.assertEqual(ponte.status()["siat"]["estado"], "disponivel")
        self.assertEqual(ponte.status()["whatsapp"]["estado"], "nao_aberto")
        ponte.ultima -= 13
        self.assertEqual(ponte.status()["siat"]["estado"], "indisponivel")

    def test_descarta_dados_extras_e_nao_troca_navegador_ativo(self):
        ponte = PonteExtensao()
        dados = estados()
        dados["estados"]["siat"]["cpf"] = "DADO-FICTICIO"
        ponte.sincronizar(dados)
        self.assertNotIn("DADO-FICTICIO", str(ponte.estados))
        with self.assertRaises(ValueError):
            ponte.sincronizar({**dados, "instancia": "outro-navegador"})

    def test_comando_emitido_uma_vez_e_limpo_apos_resposta(self):
        ponte = PonteExtensao()
        ponte.sincronizar(estados("consulta"))
        resultados = []
        thread = threading.Thread(
            target=lambda: resultados.append(ponte.executar("siat", "consultar", "TESTE-FICTICIO"))
        )
        thread.start()
        try:
            limite = time.monotonic() + 2
            while ponte.pedido is None and time.monotonic() < limite:
                time.sleep(0.01)
            comando = ponte.sincronizar(estados("consulta"))
            self.assertEqual(comando["valor"], "TESTE-FICTICIO")
            self.assertIsNone(ponte.sincronizar(estados("consulta")))
            ponte.sincronizar(
                {**estados("consulta"), "resposta": {"id": "resposta-antiga", "resultado": "vazio"}}
            )
            self.assertIsNone(ponte.pedido["resposta"])
            ponte.sincronizar(
                {
                    **estados("consulta"),
                    "resposta": {"id": comando["id"], "resultado": "atualizado"},
                }
            )
        finally:
            thread.join(timeout=10)
        self.assertEqual(resultados, ["atualizado"])
        self.assertIsNone(ponte.pedido)

    @override_settings(APP_MODE="navegador")
    def test_endpoint_exige_csrf_e_nao_aceita_corpo_arbitrario(self):
        cliente = Client(enforce_csrf_checks=True)
        self.assertEqual(
            cliente.post(
                "/api/extensao/sincronizar/", estados(), content_type="application/json"
            ).status_code,
            403,
        )
        cliente.get("/painel/")
        csrf = cliente.cookies["csrftoken"].value
        with patch("apps.atendimento.views.ponte", PonteExtensao()):
            resposta = cliente.post(
                "/api/extensao/sincronizar/",
                estados(),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=csrf,
            )
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.json(), {"comando": None})
            resposta = cliente.post(
                "/api/extensao/sincronizar/",
                [],
                content_type="application/json",
                HTTP_X_CSRFTOKEN=csrf,
            )
            self.assertEqual(resposta.status_code, 400)

    def test_recuperacao_compartilhada_repete_apenas_uma_vez(self):
        class Motor:
            pesquisas = 0
            saidas = 0
            tela = EstadoSessao.CONSULTA

            def estado(self):
                return self.tela

            def pesquisar(self, codigo):
                self.pesquisas += 1

            def vazia(self):
                return True

            def sair(self):
                self.saidas += 1
                self.tela = EstadoSessao.LOGIN

            def pausar(self):
                self.tela = EstadoSessao.CONSULTA

        motor = Motor()
        resultado = recuperar_com_motor(motor, "TESTE-FICTICIO", lambda texto: None)
        self.assertEqual(resultado, ResultadoConsulta.CONFERIR_MANUALMENTE)
        self.assertEqual((motor.pesquisas, motor.saidas), (2, 1))
