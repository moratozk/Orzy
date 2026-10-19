"""Entrar com o Mercado Livre, a sessão na memória (o único cookie do site) e sair."""

from unittest import mock

import ml_api
from contas.models import Conta
from contas.sessoes import GUARDADAS
from django.db import connection
from relatorios.historico import HISTORICO

from .base import CLIENT_ID, CONTA, SECRET, Navegador, SistemaBase, codigo_guardado


class LoginTests(SistemaBase):
    def conferir_cookie(self, cookie):
        self.assertTrue(cookie["httponly"])
        self.assertTrue(cookie["secure"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(str(cookie["max-age"]), "28800", "8 horas")
        self.assertEqual(cookie["path"], "/")

    def test_entrar_leva_ao_mercado_livre_com_pkce_e_estado(self):
        resposta = self.abrir("/entrar")
        self.assertEqual(resposta.status_code, 302)
        destino = resposta["Location"]
        self.assertTrue(destino.startswith(ml_api.AUTH_URL))
        for pedaco in ("code_challenge_method=S256", "state=", "redirect_uri=https%3A%2F%2Forzy.test%2Fretorno",
                       f"client_id={CLIENT_ID}"):
            self.assertIn(pedaco, destino)
        self.assertNotIn(SECRET, destino)
        self.conferir_cookie(resposta.cookies["orzy_sessao"])
        self.assertEqual(set(resposta.cookies), {"orzy_sessao"}, "o único cookie do site")

    def test_retorno_com_estado_trocado_nao_troca_o_codigo(self):
        self.abrir("/entrar")
        resposta = self.abrir("/retorno?code=TG-falso&state=outro")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("não é válido", self.texto(resposta))
        self.assertEqual(self.chamadas_de_token(), [])
        self.assertEqual(HISTORICO.ler_contagens(), {}, "login que não terminou não conta")

    def test_retorno_sem_ter_clicado_em_conectar(self):
        resposta = self.abrir("/retorno?code=TG-x&state=y")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("Sua sessão expirou", self.texto(resposta))

    def test_quem_nao_autoriza_ve_o_aviso(self):
        destino = self.abrir("/entrar")["Location"]
        estado = dict(p.split("=", 1) for p in destino.split("?", 1)[1].split("&"))["state"]
        resposta = self.abrir(f"/retorno?error=access_denied&state={estado}")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("Você não autorizou o acesso", self.texto(resposta))

    def test_login_guarda_o_token_na_memoria_e_o_codigo_de_renovacao_cifrado_no_banco(self):
        self.entrar()
        sessao = self.sessao()
        self.assertEqual(sessao["usuario"], {"id": CONTA, "apelido": "LOJA_TESTE"})
        tokens = sessao["cliente"].tokens
        self.assertNotIn("refresh_token", tokens)
        self.assertFalse(ml_api.ARQ_TOKENS.exists(), "o login do site não pode ir para o disco")
        self.assertFalse(ml_api.ARQ_CONFIG.exists())
        self.assertEqual(set(self.client.cookies), {"orzy_sessao"}, "nem o código contra pedidos de outros sites")
        self.assertNotIn(tokens["access_token"], self.client.cookies["orzy_sessao"].value)
        self.assertNotIn("django_session", connection.introspection.table_names(), "nenhuma sessão vai para o banco")

        conta = Conta.objects.get(ml_user_id=CONTA)
        self.assertEqual(conta.apelido, "LOJA_TESTE")
        codigo = codigo_guardado()
        self.assertTrue(self.ml.refresh_ainda_vale(codigo), "o código guardado é o que o Mercado Livre mandou")
        # Nem o código de renovação nem o token de acesso aparecem abertos em alguma tabela.
        with connection.cursor() as cursor:
            for tabela in connection.introspection.table_names():
                cursor.execute("SELECT * FROM " + connection.ops.quote_name(tabela))
                linhas = repr(cursor.fetchall())
                self.assertNotIn(codigo, linhas, tabela)
                self.assertNotIn(tokens["access_token"], linhas, tabela)

    def test_login_troca_o_codigo_da_sessao(self):
        resposta = self.abrir("/entrar")
        antes = resposta.cookies["orzy_sessao"].value
        resposta = self.abrir(self.ml.autorizar(resposta["Location"])[len("https://orzy.test"):])
        self.assertEqual((resposta.status_code, resposta["Location"]), (302, "/relatorio"))
        self.conferir_cookie(resposta.cookies["orzy_sessao"])
        self.assertNotEqual(resposta.cookies["orzy_sessao"].value, antes)

        com_o_de_antes = Navegador()
        com_o_de_antes.cookies["orzy_sessao"] = antes
        self.assertEqual(self.abrir("/relatorio", com_o_de_antes).status_code, 302,
                         "o código de antes do login não entra")
        self.assertEqual(self.abrir("/relatorio").status_code, 200)

    def test_entrar_de_novo_encerra_a_sessao_de_antes(self):
        self.entrar()
        antes = self.client.cookies["orzy_sessao"].value
        self.abrir("/entrar")
        self.assertIsNone(GUARDADAS.obter(antes))

    def test_sem_login_volta_para_o_inicio(self):
        for caminho in ("/relatorio", "/relatorio/abc", "/historico", "/historico/1", "/conta"):
            resposta = self.abrir(caminho)
            self.assertEqual((resposta.status_code, resposta["Location"]), (302, "/"), caminho)

    def test_sair_encerra_a_sessao(self):
        self.entrar()
        chave = self.client.cookies["orzy_sessao"].value
        resposta = self.enviar("/sair")
        self.assertEqual((resposta.status_code, resposta["Location"]), (302, "/"))
        self.assertIsNone(GUARDADAS.obter(chave))
        self.assertEqual(str(resposta.cookies["orzy_sessao"]["max-age"]), "0", "o navegador apaga o cookie")

    def test_sair_sem_o_codigo_do_formulario_e_recusado(self):
        self.entrar()
        resposta = self.enviar("/sair", com_codigo=False)
        self.assertEqual(resposta.status_code, 403)
        self.assertIn("Pedido recusado", self.texto(resposta))
        self.assertTrue(self.sessao(), "a sessão continua")

    def test_pedido_de_outro_site_sem_login_volta_para_o_inicio(self):
        # Quem deixou a página aberta até a sessão acabar e clicou num botão.
        resposta = self.enviar("/relatorio/gerar", {"dias": 30}, origem="https://site-estranho.example")
        self.assertEqual((resposta.status_code, resposta["Location"]), (302, "/"))

    def test_sessao_acaba_8_horas_depois_do_login_mesmo_em_uso(self):
        relogio = [1_000_000.0]
        with mock.patch.object(GUARDADAS, "agora", lambda: relogio[0]):
            self.entrar()
            for _ in range(7):
                relogio[0] += 3600
                self.assertEqual(self.abrir("/relatorio").status_code, 200)
            relogio[0] += 3599
            self.assertEqual(self.abrir("/relatorio").status_code, 200, "1 segundo antes das 8 horas")
            relogio[0] += 2
            self.assertEqual(self.abrir("/relatorio").status_code, 302, "8 horas depois do login")
