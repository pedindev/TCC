from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from apps.atendimento.desktop import MotorDesktop, NavegadorDesktop
from apps.atendimento.erros import FalhaOperacao
from apps.siat.recuperacao import ResultadoConsulta, recuperar_com_motor


class DesktopTests(SimpleTestCase):
    def test_preparacao_preserva_login_manual_e_aceita_tela_ja_livre(self):
        for resposta in ("login", "sem_detalhes", "detalhes_fechados"):
            with self.subTest(resposta=resposta):
                transporte = Mock()
                transporte.chamar.return_value = {"resultado": resposta}
                motor = MotorDesktop(NavegadorDesktop(transporte), "aba-ficticia", Mock())
                motor.preparar_consulta()
                transporte.chamar.assert_called_once_with("preparar_consulta", "aba-ficticia", "")

    def test_preparacao_ambigua_interrompe_antes_de_pesquisar(self):
        transporte = Mock()
        transporte.chamar.side_effect = [
            {"siat": {"estado": "detalhes", "referencia": "aba-ficticia"}},
            {"resultado": "ok"},
            {"resultado": "fechar_ambiguo"},
        ]
        with patch("apps.atendimento.desktop.time.sleep"), self.assertRaises(FalhaOperacao) as erro:
            NavegadorDesktop(transporte).consultar("FICTICIO", Mock(), Mock())
        self.assertEqual(erro.exception.codigo, "fechar_detalhes")
        self.assertEqual(
            [c.args[0] for c in transporte.chamar.call_args_list],
            ["status", "ativar", "preparar_consulta"],
        )

    def test_colagem_transmite_texto_integral_sem_alterar(self):
        transporte = Mock()
        transporte.chamar.return_value = {"resultado": "ok"}
        texto = "Orientação fictícia\n\n➡️ https://example.invalid/\n*Confira os dados*"
        NavegadorDesktop(transporte).colar(texto)
        transporte.chamar.assert_called_once_with("colar", valor=texto)

    def test_falhas_antes_da_colagem_explicam_a_causa_e_permitem_nova_tentativa(self):
        for status, trecho in (
            ("campo_nao_identificado", "não foi reconhecido"),
            ("campo_nao_legivel", "conferir o campo"),
            ("campo_ocupado", "já contém texto"),
            ("clipboard_indisponivel", "transferência"),
            ("tecla_pressionada", "tecla"),
            ("falha_pre_colagem", "preparação"),
        ):
            with self.subTest(status=status):
                transporte = Mock()
                transporte.chamar.return_value = {"resultado": status}
                with self.assertRaises(FalhaOperacao) as erro:
                    NavegadorDesktop(transporte).colar("FICTÍCIO")
                self.assertEqual(erro.exception.codigo, "campo_sem_foco")
                self.assertIn(trecho, erro.exception.mensagem)
                transporte.chamar.assert_called_once()

    def test_retorno_painel_tenta_uma_vez(self):
        transporte = Mock()
        transporte.chamar.return_value = {"resultado": "ok"}
        self.assertTrue(NavegadorDesktop(transporte).retornar_painel())
        transporte.chamar.assert_called_once_with("retornar_painel")

    def test_retorno_indisponivel_nao_propaga_erro(self):
        for resposta in ("foco", "painel_indisponivel"):
            transporte = Mock()
            transporte.chamar.return_value = {"resultado": resposta}
            self.assertFalse(NavegadorDesktop(transporte).retornar_painel())
        transporte.chamar.side_effect = FalhaOperacao("conexao", "Falha", "Confira")
        self.assertFalse(NavegadorDesktop(transporte).retornar_painel())

    def test_le_apenas_descricao_de_resposta_confirmada(self):
        transporte = Mock()
        transporte.chamar.return_value = {
            "resultado": "retencao_lida",
            "descricao": "ICMS / SIMEI pendente",
        }
        motor = MotorDesktop(NavegadorDesktop(transporte), "aba-ficticia", Mock())
        resultado = motor.ler_retencao("TESTE")
        self.assertEqual(resultado.motivo, "simei")
        self.assertEqual(resultado.descricao_retencao, "ICMS / SIMEI pendente")
        transporte.chamar.assert_called_once_with("retencao", "aba-ficticia", "TESTE")

    def test_falha_leitura_nao_usa_descricao_recebida(self):
        for status in ("campo_ambiguo", "foco", "demora", "resultado_nao_confirmado"):
            transporte = Mock()
            transporte.chamar.return_value = {"resultado": status, "descricao": "SIMEI"}
            motor = MotorDesktop(NavegadorDesktop(transporte), "aba-ficticia", Mock())
            with self.subTest(status=status), self.assertRaises(FalhaOperacao):
                motor.ler_retencao("TESTE")

    def test_lupa_nao_aciona_sem_resposta_atualizada(self):
        transporte = Mock()
        motor = MotorDesktop(NavegadorDesktop(transporte), "aba-ficticia", lambda: None)
        for resultado in (None, "vazio", "incerto"):
            motor.resultado = resultado
            with self.assertRaises(FalhaOperacao):
                motor.abrir_detalhes("TESTE")
        transporte.chamar.assert_not_called()

    def test_lupa_usa_rastreio_corrente_e_recusa_resultado_ambiguo(self):
        transporte = Mock()
        transporte.chamar.return_value = {"resultado": "linha_ambigua"}
        motor = MotorDesktop(NavegadorDesktop(transporte), "aba-ficticia", lambda: None)
        motor.resultado = "atualizado"
        with self.assertRaises(FalhaOperacao) as erro:
            motor.abrir_detalhes("TESTE")
        self.assertEqual(erro.exception.codigo, "detalhes_indisponiveis")
        transporte.chamar.assert_called_once_with("detalhes", "aba-ficticia", "TESTE")

    def test_status_localiza_individualmente_sem_ativar_janelas(self):
        transporte = Mock()
        transporte.chamar.return_value = {
            "siat": {"estado": "ausente"},
            "whatsapp": {"estado": "localizada"},
        }
        navegador = NavegadorDesktop(transporte)
        estados = navegador.status()
        self.assertEqual(estados["siat"]["estado"], "nao_aberto")
        self.assertIn("login será conferido", estados["whatsapp"]["texto"])
        navegador.status()
        transporte.chamar.assert_called_once_with("status")

    def test_falha_nao_mantem_estados_antigos(self):
        transporte = Mock()
        transporte.chamar.side_effect = FalhaOperacao("conexao", "Falha", "Confira")
        navegador = NavegadorDesktop(transporte)
        self.assertEqual(navegador.status()["siat"]["estado"], "indisponivel")

    def test_sem_aba_nao_ativa_nem_consulta(self):
        transporte = Mock()
        transporte.chamar.return_value = {"siat": {"estado": "duplicada"}}
        navegador = NavegadorDesktop(transporte)
        with self.assertRaises(FalhaOperacao):
            navegador.consultar("TESTE", Mock(), Mock())
        transporte.chamar.assert_called_once_with("status")

    def test_perda_de_foco_interrompe(self):
        transporte = Mock()
        transporte.chamar.return_value = {"resultado": "foco"}
        navegador = NavegadorDesktop(transporte)
        verificar = Mock()
        motor = MotorDesktop(navegador, "aba-ficticia", verificar)
        with self.assertRaises(FalhaOperacao):
            motor.pesquisar("TESTE")
        verificar.assert_called_once()
        transporte.chamar.assert_called_once_with("consultar", "aba-ficticia", "TESTE")

    def test_colagem_incerta_nao_repete(self):
        transporte = Mock()
        transporte.chamar.return_value = {"resultado": "incerto"}
        with self.assertRaises(FalhaOperacao) as erro:
            NavegadorDesktop(transporte).colar("TEXTO FICTICIO")
        self.assertEqual(erro.exception.codigo, "colagem_incerta")
        transporte.chamar.assert_called_once_with("colar", valor="TEXTO FICTICIO")

    def test_motor_windows_reaproveita_recuperacao_sem_loop(self):
        transporte = Mock()
        # Estado inicial, estado do ciclo, consulta vazia, estado após consulta,
        # sair, aguardar login (já concluído no cenário), estado, consulta, estado.
        respostas = [
            "consulta",
            "consulta",
            "vazio",
            "consulta",
            "ok",
            "consulta",
            "consulta",
            "vazio",
            "consulta",
        ]
        transporte.chamar.side_effect = [{"resultado": r} for r in respostas]
        motor = MotorDesktop(NavegadorDesktop(transporte), "aba-ficticia", lambda: None)
        with patch("apps.atendimento.desktop.time.sleep"):
            resultado = recuperar_com_motor(motor, "TESTE", lambda texto: None)
        self.assertEqual(resultado, ResultadoConsulta.CONFERIR_MANUALMENTE)
        acoes = [c.args[0] for c in transporte.chamar.call_args_list]
        self.assertEqual(acoes.count("sair"), 1)
        self.assertEqual(acoes.count("consultar"), 2)
