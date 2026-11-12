from django.test import SimpleTestCase

from apps.atendimento.erros import FalhaOperacao
from apps.siat.resultado import resultado_da_retencao


class RetencaoTests(SimpleTestCase):
    def test_palavras_em_descricoes_completas_preservam_original(self):
        casos = {
            "  ICMS - SIMEI / conferência pendente  ": "simei",
            "SIMEI — imposto não recolhido": "simei",
            "COMERCIALIZAÇÃO — quantidade e habitualidade": "comercializacao",
            "Recolhimento DIFAL pendente": "difal",
            "E-commerce: imposto pendente": "difal",
            "comércio eletrônico / eCommerce": "difal",
            "Mercadoria sem nota fiscal": "sem_nota_fiscal",
            "MERCADORIA SEM NOTA": "sem_nota_fiscal",
            "Mercadorias sem nota — conferir documento": "sem_nota_fiscal",
            "Ausência de nota fiscal": "sem_nota_fiscal",
            "Mercadorias desacompanhadas de notas fiscais": "sem_nota_fiscal",
            "Irregularidades fiscais — verificar cadastro": "irregularidades_fiscais",
            "Situação fiscal irregular": "irregularidades_fiscais",
        }
        for texto, categoria in casos.items():
            with self.subTest(texto=texto):
                resultado = resultado_da_retencao(texto)
                resultado.validar()
                self.assertEqual(resultado.descricao_retencao, texto)
                self.assertEqual(resultado.motivo, categoria)
                self.assertEqual(resultado.situacao, "retida")

    def test_desconhecido_ambiguo_ou_negado_preserva_sem_categoria(self):
        for texto in (
            "Documentação a conferir",
            "ICMS",
            "SIMEI e comercialização",
            "não se trata de SIMEI",
            "SIMEI: não se aplica",
            "XSIMEIX",
            "DIFALXYZ",
            "Com nota fiscal",
            "Não é mercadoria sem nota",
            "MERCADORIA SEM NOTAVEL",
        ):
            with self.subTest(texto=texto):
                resultado = resultado_da_retencao(texto)
                resultado.validar()
                self.assertEqual(resultado.motivo, "")
                self.assertEqual(resultado.descricao_retencao, texto)

    def test_campo_vazio_ou_invalido_nao_confirma_retencao(self):
        for texto in (None, "", " \n ", 42, "X" * 251):
            with self.subTest(texto=texto), self.assertRaises(FalhaOperacao) as erro:
                resultado_da_retencao(texto)
            self.assertEqual(erro.exception.codigo, "inconclusivo")
