from django.db import IntegrityError, transaction
from django.db.models import Max
from django.test import TestCase

from apps.catalogo.models import GuiaPortal, Orientacao


class CatalogoTests(TestCase):
    def test_instalacao_nova_cadastra_cinco_orientacoes_ainda_nao_revisadas(self):
        versoes = Orientacao.objects.values("codigo").annotate(ultima=Max("versao"))
        orientacoes = [
            Orientacao.objects.get(codigo=item["codigo"], versao=item["ultima"]) for item in versoes
        ]
        self.assertEqual(len(orientacoes), 5)
        self.assertEqual({o.categoria for o in orientacoes}, set(Orientacao.Categoria.values))
        for orientacao in orientacoes:
            with self.subTest(codigo=orientacao.codigo):
                self.assertEqual(orientacao.estado, Orientacao.Estado.RASCUNHO)
                self.assertIsNone(orientacao.revisado_em)
                self.assertTrue(orientacao.fontes)
                self.assertNotIn("Olá", orientacao.texto)
                self.assertTrue(orientacao.texto.startswith("Sua mercadoria está retida porque"))
                self.assertNotIn("[CÓDIGO DE RASTREIO]", orientacao.texto)
                self.assertNotIn("https://", orientacao.texto)
                if orientacao.codigo == "SNF-01":
                    self.assertIn("por este WhatsApp", orientacao.texto)
                    self.assertNotIn("avulsa", orientacao.texto)
                    self.assertNotIn("rastreio", orientacao.texto)

    def test_textos_anteriores_preservados_como_historico(self):
        self.assertEqual(Orientacao.objects.filter(versao=1).exclude(codigo="IRF-01").count(), 4)

    def test_guias_comuns_apontam_para_os_dois_canais_sem_dados_de_atendimento(self):
        self.assertEqual(GuiaPortal.objects.count(), 31)
        abertura = GuiaPortal.objects.get(codigo="SAC-ABERTURA", versao=3)
        acompanhamento = GuiaPortal.objects.get(codigo="SAC-ACOMPANHAMENTO", versao=3)
        self.assertIn("servico-de-atendimento-ao-cidadao-sac", abertura.url)
        self.assertEqual(
            acompanhamento.url, "https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao"
        )
        self.assertIn("Não foi satisfatória. Desejo receber atendimento humano", abertura.texto)
        self.assertIn("GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS", abertura.texto)
        self.assertIn("protocolo e o código de acesso", acompanhamento.texto)
        self.assertEqual(abertura.estado, Orientacao.Estado.RASCUNHO)
        self.assertEqual(acompanhamento.estado, Orientacao.Estado.RASCUNHO)

    def test_novos_guias_preservam_historico_e_origem_sem_aprovar_textos(self):
        self.assertEqual(
            GuiaPortal.objects.filter(
                codigo__in=["SAC-ABERTURA", "SAC-ACOMPANHAMENTO"], versao=1
            ).count(),
            2,
        )
        pedidos = GuiaPortal.objects.filter(codigo__startswith="SAC-PEDIDO-")
        self.assertEqual(pedidos.count(), 25)
        for pedido in pedidos:
            with self.subTest(codigo=pedido.codigo):
                aprovado = (
                    pedido.versao in {2, 3}
                    and pedido.codigo
                    in {
                        "SAC-PEDIDO-GERAL",
                        "SAC-PEDIDO-COM",
                        "SAC-PEDIDO-SIM",
                        "SAC-PEDIDO-DIF",
                    }
                ) or (pedido.codigo, pedido.versao) in {
                    ("SAC-PEDIDO-IRF", 4),
                    ("SAC-PEDIDO-NFA", 5),
                }
                self.assertEqual(
                    pedido.estado,
                    Orientacao.Estado.REVISADO if aprovado else Orientacao.Estado.RASCUNHO,
                )
                if pedido.codigo == "SAC-PEDIDO-NF" and pedido.versao >= 2:
                    pedido.full_clean()
                    self.assertEqual(pedido.url, "")
                    self.assertIn("por este WhatsApp", pedido.texto)
                elif aprovado:
                    self.assertIn("[COLOQUE SEU CÓDIGO]", pedido.texto)
                    self.assertNotIn("se for seu próprio pedido", pedido.texto)
                else:
                    self.assertIn("[CÓDIGO DE RASTREIO]", pedido.texto)
                self.assertTrue(pedido.observacoes)
                self.assertNotIn("Olá", pedido.texto)
        nota = pedidos.get(codigo="SAC-PEDIDO-NF", versao=4)
        avulsa = pedidos.get(codigo="SAC-PEDIDO-NFA", versao=5)
        self.assertIn("fornecedor", nota.texto)
        self.assertIn("até a data da postagem nos Correios", nota.texto)
        self.assertIn("comprovante de pagamento da compra da mercadoria", avulsa.texto)
        self.assertIn("[CPF]", avulsa.texto)

    def test_mesmo_codigo_e_versao_nao_podem_duplicar(self):
        orientacao = Orientacao.objects.get(codigo="COM-01", versao=1)
        orientacao.pk = None
        with self.assertRaises(IntegrityError), transaction.atomic():
            orientacao.save()
