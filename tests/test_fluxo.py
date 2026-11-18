import json
import threading
import time
from unittest.mock import Mock, patch

from django.test import Client, SimpleTestCase, TestCase

from apps.atendimento.desktop import NavegadorDesktop
from apps.atendimento.erros import FalhaOperacao
from apps.atendimento.fluxo import FluxoOperador
from apps.catalogo.models import GuiaPortal, Orientacao
from apps.catalogo.service import preparar_orientacao
from apps.siat.resultado import Resultado, resultado_da_retencao


class NavegadorFalso:
    def __init__(self):
        self.liberar = threading.Event()
        self.consultas = 0
        self.colagens = []
        self.resultado = Resultado("retida", "comercializacao", True)
        self.erro = None
        self.erro_colagem = None
        self.retornos = 0
        self.retornar_ok = True

    def status(self):
        return {
            nome: {"estado": "disponivel", "texto": "Fictício"} for nome in ("siat", "whatsapp")
        }

    def consultar(self, codigo, avisar, verificar):
        self.consultas += 1
        while not self.liberar.wait(0.01):
            verificar()
        if self.erro:
            raise self.erro
        return self.resultado

    def colar(self, texto):
        if self.erro_colagem:
            raise self.erro_colagem
        self.colagens.append(texto)

    def fechar(self):
        pass

    def retornar_painel(self):
        self.retornos += 1
        return self.retornar_ok


def catalogo_falso(resultado, *, simulado):
    return {
        "texto": "Mensagem fictícia\nhttps://example.invalid/",
        "versao": "FICTICIO v1",
        "aviso": "",
        "pode_colar": True,
    }


class FluxoTests(SimpleTestCase):
    def preparar_duas_mensagens(self):
        primeira = catalogo_falso(None, simulado=True)
        segunda = {**primeira, "texto": "Segunda mensagem fictícia\nhttps://example.invalid/avulsa"}
        self.fluxo.catalogo = lambda *args, **kwargs: {
            **primeira,
            "mensagens": [
                {**primeira, "titulo": "Enviar nota"},
                {**segunda, "titulo": "Nota avulsa"},
            ],
        }
        return self.pronto()

    def test_selecao_cola_segunda_mensagem_e_preserva_primeira(self):
        s = self.preparar_duas_mensagens()
        antiga = s["mensagem"]
        self.fluxo.selecionar_mensagem(s["atendimento"], s["token"], 1)
        s = self.fluxo.snapshot()
        self.assertEqual(s["mensagem"], s["mensagens"][1]["texto"])
        self.assertNotEqual(s["mensagem"], antiga)
        self.fluxo.colar(s["atendimento"], s["token"])
        s = self.aguardar(lambda x: not x["ocupado"])
        self.assertEqual(self.navegador.colagens, [s["mensagens"][1]["texto"]])
        self.fluxo.selecionar_mensagem(s["atendimento"], s["token"], 0)
        s = self.fluxo.snapshot()
        self.assertEqual(s["mensagem"], antiga)
        self.assertFalse(s["colagem_tentada"])
        self.fluxo.selecionar_mensagem(s["atendimento"], s["token"], 1)
        s = self.fluxo.snapshot()
        self.assertTrue(s["colagem_tentada"])
        self.fluxo.novo(s["atendimento"], s["token"])
        self.assertEqual(self.fluxo.snapshot()["mensagens"], [])

    def test_nao_troca_mensagem_durante_contagem(self):
        s = self.preparar_duas_mensagens()
        self.fluxo.colar(s["atendimento"], s["token"])
        s = self.fluxo.snapshot()
        with self.assertRaises(FalhaOperacao):
            self.fluxo.selecionar_mensagem(s["atendimento"], s["token"], 1)
        s = self.aguardar(lambda x: not x["ocupado"])
        self.assertEqual(self.navegador.colagens, [s["mensagens"][0]["texto"]])

    def test_selecao_rejeita_indices_invalidos(self):
        s = self.preparar_duas_mensagens()
        for indice in (-1, 2, True, "1", None):
            with self.subTest(indice=indice), self.assertRaises(FalhaOperacao):
                self.fluxo.selecionar_mensagem(s["atendimento"], s["token"], indice)
        self.assertEqual(self.fluxo.snapshot()["mensagem_indice"], 0)

    def setUp(self):
        self.navegador = NavegadorFalso()
        self.fluxo = FluxoOperador(
            lambda: self.navegador, modo="simulacao", catalogo=catalogo_falso, contagem=0.2
        )
        self.addCleanup(self.fluxo.fechar)

    def aguardar(self, condicao):
        limite = time.monotonic() + 3
        while time.monotonic() < limite:
            s = self.fluxo.snapshot()
            if condicao(s):
                return s
            time.sleep(0.01)
        self.fail("Fluxo fictício não chegou ao estado esperado.")

    def iniciar(self):
        s = self.fluxo.snapshot()
        self.fluxo.consultar(s["atendimento"], s["token"], "TESTE-LOGIN")
        return s

    def pronto(self):
        self.iniciar()
        self.navegador.liberar.set()
        return self.aguardar(lambda s: s["fase"] == "pronto" and not s["ocupado"])

    def test_consulta_unica_inclusive_entre_abas_e_repeticao(self):
        antigo = self.iniciar()
        for s in (antigo, self.fluxo.snapshot()):
            with self.assertRaises(FalhaOperacao):
                self.fluxo.consultar(s["atendimento"], s["token"], "TESTE-DIF")
        self.navegador.liberar.set()
        self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(self.navegador.consultas, 1)

    def test_novo_invalida_resultado_tardio_e_limpa_caso(self):
        self.iniciar()
        s = self.fluxo.snapshot()
        self.fluxo.novo(s["atendimento"], s["token"])
        self.navegador.liberar.set()
        s = self.aguardar(lambda s: not s["ocupado"])
        for campo in ("rastreio", "situacao", "motivo", "mensagem"):
            self.assertEqual(s[campo], "")
        self.assertEqual(s["fase"], "inicial")

    def test_colagem_uma_vez_e_replay_recusado(self):
        s = self.pronto()
        self.fluxo.colar(s["atendimento"], s["token"])
        with self.assertRaises(FalhaOperacao):
            self.fluxo.colar(s["atendimento"], s["token"])
        s = self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(s["fase"], "colado")
        self.assertEqual(self.navegador.colagens, [s["mensagem"]])
        with self.assertRaises(FalhaOperacao):
            self.fluxo.colar(s["atendimento"], s["token"])

    def test_falha_colagem_preserva_mensagem_e_so_libera_retry_se_nao_colou(self):
        s = self.pronto()
        self.navegador.erro_colagem = FalhaOperacao(
            "campo_sem_foco", "Campo não reconhecido", "Confira"
        )
        self.fluxo.colar(s["atendimento"], s["token"])
        s = self.aguardar(lambda estado: not estado["ocupado"])
        self.assertFalse(s["colagem_tentada"])
        self.assertTrue(s["mensagem"])
        self.navegador.erro_colagem = FalhaOperacao("colagem_incerta", "Confira", "Confira")
        self.fluxo.colar(s["atendimento"], s["token"])
        s = self.aguardar(lambda estado: not estado["ocupado"])
        self.assertTrue(s["colagem_tentada"])
        self.assertTrue(s["mensagem"])
        with self.assertRaises(FalhaOperacao):
            self.fluxo.colar(s["atendimento"], s["token"])

    def test_cancelar_contagem_preserva_mensagem_sem_colar(self):
        s = self.pronto()
        self.fluxo.colar(s["atendimento"], s["token"])
        s = self.fluxo.snapshot()
        self.fluxo.cancelar_colagem(s["atendimento"], s["token"])
        final = self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(final["mensagem"], s["mensagem"])
        self.assertEqual(self.navegador.colagens, [])

    def test_novo_durante_contagem_nao_cola_mensagem_antiga(self):
        s = self.pronto()
        self.fluxo.colar(s["atendimento"], s["token"])
        s = self.fluxo.snapshot()
        self.fluxo.novo(s["atendimento"], s["token"])
        self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(self.navegador.colagens, [])

    def test_whatsapp_indisponivel_mantem_orientacao(self):
        s = self.pronto()
        with self.fluxo.lock:
            self.fluxo.sistemas["whatsapp"]["estado"] = "indisponivel"
        with self.assertRaises(FalhaOperacao):
            self.fluxo.colar(s["atendimento"], s["token"])
        self.assertEqual(self.fluxo.snapshot()["mensagem"], s["mensagem"])

    def test_motivo_desconhecido_nao_seleciona_irregularidade(self):
        self.navegador.resultado = Resultado("retida", "outro", True)
        self.iniciar()
        self.navegador.liberar.set()
        s = self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(s["erro"], "motivo_desconhecido")
        self.assertEqual(s["situacao"], "retida")
        self.assertEqual(s["mensagem"], "")

    def test_descricao_completa_com_orientacao(self):
        self.navegador.resultado = resultado_da_retencao("SIMEI — ICMS pendente")
        s = self.pronto()
        self.assertEqual(s["motivo"], "SIMEI — ICMS pendente")
        self.assertTrue(s["pode_colar"])
        self.assertIn("Mensagem fictícia", s["mensagem"])
        self.assertEqual(self.navegador.retornos, 1)

    def test_falha_retorno_nao_apaga_resultado_nem_orientacao(self):
        self.navegador.retornar_ok = False
        s = self.pronto()
        self.assertEqual(s["situacao"], "retida")
        self.assertTrue(s["mensagem"])
        self.assertFalse(s["erro"])
        self.assertIn("Volte à aba", s["acao"])

    def test_descricao_desconhecida_sem_orientacao_nao_e_erro(self):
        self.navegador.resultado = resultado_da_retencao("Documento a conferir")
        self.fluxo.catalogo = Mock(side_effect=AssertionError("Não deve escolher categoria"))
        s = self.pronto()
        self.assertEqual(s["motivo"], "Documento a conferir")
        self.assertEqual(s["situacao"], "retida")
        self.assertEqual(s["mensagem"], "")
        self.assertFalse(s["pode_colar"])
        self.assertFalse(s["erro"])
        self.fluxo.catalogo.assert_not_called()
        self.assertEqual(self.navegador.retornos, 1)

    def test_orientacao_ausente_preserva_descricao(self):
        self.navegador.resultado = resultado_da_retencao("SIMEI — informação fictícia")
        self.fluxo.catalogo = Mock(side_effect=FalhaOperacao("orientacao_indisponivel", "", ""))
        s = self.pronto()
        self.assertEqual(s["motivo"], "SIMEI — informação fictícia")
        self.assertFalse(s["erro"])
        self.assertFalse(s["pode_colar"])
        self.assertEqual(s["mensagem"], "")
        self.fluxo.novo(s["atendimento"], s["token"])
        self.assertEqual(self.fluxo.snapshot()["motivo"], "")

    def test_resultado_incompativel_nao_exibe_liberada(self):
        self.navegador.resultado = Resultado("liberada", "difal", True)
        self.iniciar()
        self.navegador.liberar.set()
        s = self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(s["situacao"], "")
        self.assertEqual(s["erro"], "inconclusivo")

    def test_excecao_nao_expoe_conteudo(self):
        self.navegador.erro = RuntimeError("MARCADOR-PRIVADO")
        self.iniciar()
        self.navegador.liberar.set()
        s = self.aguardar(lambda s: not s["ocupado"])
        self.assertNotIn("MARCADOR-PRIVADO", json.dumps(s))
        self.assertEqual(s["erro"], "falha_interna")

    def test_prazo_cancela_consulta_sem_liberar_segunda_antes_de_terminar(self):
        self.fluxo.prazo = 0.1
        self.iniciar()
        s = self.aguardar(lambda s: not s["ocupado"])
        self.assertEqual(s["erro"], "demora")

    def test_expiracao_descarta_dados_e_invalida_token(self):
        s = self.pronto()
        with self.fluxo.lock:
            self.fluxo.ultima_atividade -= 1000
        novo = self.fluxo.snapshot()
        self.assertEqual(novo["mensagem"], "")
        self.assertNotEqual(novo["atendimento"], s["atendimento"])

    def test_api_csrf_formato_e_tokens(self):
        cliente = Client(enforce_csrf_checks=True)
        with patch("apps.atendimento.views.obter_fluxo", return_value=self.fluxo):
            cliente.get("/painel/")
            s = cliente.get("/api/estado/").json()
            corpo = {"atendimento": s["atendimento"], "token": s["token"], "codigo": "TESTE-COM"}
            self.assertEqual(cliente.post("/api/consultar/", corpo).status_code, 403)
            cabecalhos = {"HTTP_X_CSRFTOKEN": cliente.cookies["csrftoken"].value}
            self.assertEqual(
                cliente.post(
                    "/api/consultar/", "[]", content_type="application/json", **cabecalhos
                ).status_code,
                400,
            )
            r = cliente.post(
                "/api/consultar/", json.dumps(corpo), content_type="application/json", **cabecalhos
            )
            self.assertEqual(r.status_code, 202)
            self.assertEqual(
                cliente.post(
                    "/api/consultar/",
                    json.dumps(corpo),
                    content_type="application/json",
                    **cabecalhos,
                ).status_code,
                409,
            )


class CatalogoOperadorTests(TestCase):
    def test_sem_nota_oferece_avulsa_separada_com_texto_do_banco(self):
        item = preparar_orientacao(Resultado("retida", "sem_nota_fiscal", True))
        self.assertEqual(len(item["mensagens"]), 2)
        self.assertNotIn("avulsa", item["texto"])
        avulsa = item["mensagens"][1]
        guia = GuiaPortal.objects.filter(codigo="SAC-PEDIDO-NFA").order_by("-versao").first()
        self.assertEqual(avulsa["texto"], guia.texto)
        self.assertIn("comprovante de pagamento", avulsa["texto"])
        self.assertIn("dados do destinatário", avulsa["texto"])
        self.assertTrue(avulsa["pode_colar"])

    def test_avulsa_indisponivel_nao_esconde_primeira_nem_usa_versao_antiga(self):
        GuiaPortal.objects.filter(codigo="SAC-PEDIDO-NFA", versao=5).update(texto="")
        item = preparar_orientacao(Resultado("retida", "sem_nota_fiscal", True))
        self.assertTrue(item["texto"])
        self.assertTrue(item["mensagens"][0]["pode_colar"])
        self.assertEqual(item["mensagens"][1]["texto"], "")
        self.assertFalse(item["mensagens"][1]["pode_colar"])

    def test_texto_do_banco_chega_integral_ao_transporte_whatsapp(self):
        mensagem = preparar_orientacao(Resultado("retida", "simei", True))
        transporte = Mock()
        transporte.chamar.return_value = {"resultado": "ok"}
        NavegadorDesktop(transporte).colar(mensagem["texto"])
        transporte.chamar.assert_called_once_with("colar", valor=mensagem["texto"])
        self.assertIn("SOLICITE O BOLETO", mensagem["texto"])
        self.assertIn("https://portal.sefaz.pi.gov.br/", mensagem["texto"])

    def test_cinco_categorias_usam_ultima_versao_e_preservam_rascunhos(self):
        for categoria in Orientacao.Categoria.values:
            with self.subTest(categoria=categoria):
                resultado = Resultado("retida", categoria, True)
                texto = preparar_orientacao(resultado)
                self.assertTrue(texto["pode_colar"])
                self.assertIn("rascunho", texto["aviso"])
                self.assertIn("Sua mercadoria está retida porque", texto["texto"])
                demo = preparar_orientacao(resultado, simulado=True)
                self.assertTrue(demo["pode_colar"])
                self.assertTrue(demo["texto"].startswith("[SIMULAÇÃO"))
        self.assertFalse(Orientacao.objects.filter(estado="revisado").exists())

    def test_vigencia_vencida_ou_futura_bloqueia_colagem(self):
        from datetime import timedelta

        from django.utils import timezone

        hoje = timezone.localdate()
        for campos in (
            {"vigencia_inicio": hoje + timedelta(days=1), "vigencia_fim": None},
            {"vigencia_inicio": None, "vigencia_fim": hoje - timedelta(days=1)},
        ):
            with self.subTest(campos=campos):
                Orientacao.objects.filter(codigo="SIM-01", versao=4).update(**campos)
                item = preparar_orientacao(Resultado("retida", "simei", True))
                self.assertFalse(item["pode_colar"])
                self.assertIn("vigência", item["aviso"])

    def test_nota_fiscal_nao_acrescenta_avulsa_automaticamente(self):
        texto = preparar_orientacao(Resultado("retida", "sem_nota_fiscal", True))["texto"]
        self.assertNotIn("avulsa", texto)
        self.assertIn("fornecedor", texto)

    def test_guia_ausente_nao_usa_historico(self):
        GuiaPortal.objects.filter(codigo="SAC-PEDIDO-COM", versao=3).update(texto="")
        with self.assertRaises(FalhaOperacao) as erro:
            preparar_orientacao(Resultado("retida", "comercializacao", True))
        self.assertEqual(erro.exception.codigo, "orientacao_indisponivel")

    def test_mensagem_completa_mantem_links(self):
        texto = preparar_orientacao(Resultado("retida", "difal", True))["texto"]
        self.assertIn("https://portal.sefaz.pi.gov.br/servicos-institucional", texto)
        self.assertIn("https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao", texto)
