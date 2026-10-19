"""A conta e o acesso guardado: o cofre, o Conectar que cria a conta, a renovação um de cada vez, a conferência de
todo dia, as contas que perderam o acesso, a página "Sua conta" e o "Desconectar e apagar tudo"."""

import threading
from datetime import timedelta
from unittest import mock

import ml_api
from contas import acesso, cofre, login
from contas.models import Conta
from contas.views import APAGADA, APAGADA_SEM_O_MERCADO_LIVRE
from django.db import DatabaseError, connections
from django.test import SimpleTestCase
from relatorios import datas
from relatorios.geracao import PRONTO
from relatorios.historico import HISTORICO
from relatorios.models import AnuncioGuardado, RelatorioGuardado

from .base import CHAVE, CONTA, LINHA, URL, Navegador, SistemaBase, codigo_guardado, com_configuracao, criar_conta


def sem_codigo_de_renovacao_no_login():
    """O Mercado Livre sem o fluxo Refresh Token no app: o login vem sem o código de renovação."""
    trocar = ml_api.trocar_code_por_token

    def sem_renovacao(*args, **kwargs):
        tokens = trocar(*args, **kwargs)
        tokens.pop("refresh_token")
        return tokens

    return mock.patch.object(ml_api, "trocar_code_por_token", sem_renovacao)


class CofreTests(SimpleTestCase):
    def test_fecha_e_abre_com_a_mesma_chave_e_a_mesma_conta(self):
        fechado = cofre.fechar(CHAVE, CONTA, "TG-codigo-de-renovacao")
        versao, numero, _ = fechado.split(":")
        self.assertEqual(versao, "v1")
        self.assertRegex(numero, r"^[0-9a-f]{8}$")
        self.assertEqual(numero, cofre.numero_da_chave(CHAVE))
        self.assertNotIn("codigo-de-renovacao", fechado)
        self.assertEqual(cofre.abrir(CHAVE, CONTA, fechado), "TG-codigo-de-renovacao")
        self.assertNotEqual(cofre.fechar(CHAVE, CONTA, "TG-codigo-de-renovacao"), fechado,
                            "cada vez com 12 bytes sorteados")

    def test_nao_abre_com_outra_chave_em_outra_conta_nem_mexido(self):
        fechado = cofre.fechar(CHAVE, CONTA, "TG-codigo-de-renovacao")
        with self.assertRaises(cofre.OutraChave):
            cofre.abrir(bytes(32), CONTA, fechado)
        with self.assertRaises(cofre.ErroCofre, msg="o valor de uma conta copiado para a linha de outra"):
            cofre.abrir(CHAVE, CONTA + 1, fechado)
        versao, numero, cifra = fechado.split(":")
        trocado = cifra[:20] + ("B" if cifra[20] == "A" else "A") + cifra[21:]
        for estragado in (f"{versao}:{numero}:{trocado}", f"{versao}:{numero}:{cifra[:-4]}",
                          f"{versao}:{numero}:AAAA", f"v2:{numero}:{cifra}", f"{versao}:{numero}", ""):
            with self.assertRaises(cofre.ErroCofre, msg=estragado):
                cofre.abrir(CHAVE, CONTA, estragado)


class ConectarTests(SistemaBase):
    def test_conectar_cria_a_conta_e_conectar_de_novo_atualiza_a_mesma(self):
        self.entrar()
        conta = Conta.objects.get(ml_user_id=CONTA)
        self.assertEqual(conta.apelido, "LOJA_TESTE")
        self.assertIsNotNone(conta.acesso_salvo_em)
        self.assertIsNone(conta.sem_acesso_desde)
        primeiro = codigo_guardado()

        # Perdeu o acesso há uma semana, trocou o apelido no Mercado Livre e conectou de novo.
        semana_passada = datas.agora() - timedelta(days=7)
        Conta.objects.filter(pk=conta.pk).update(acesso="", sem_acesso_desde=semana_passada,
                                                 conectada_em=semana_passada)
        self.ml.usuario["nickname"] = "LOJA_NOVA"
        self.entrar(Navegador())
        self.assertEqual(Conta.objects.count(), 1)
        nova = Conta.objects.get(ml_user_id=CONTA)
        self.assertEqual((nova.pk, nova.criada_em, nova.apelido), (conta.pk, conta.criada_em, "LOJA_NOVA"))
        self.assertGreater(nova.conectada_em, semana_passada)
        self.assertIsNone(nova.sem_acesso_desde)
        self.assertNotEqual(codigo_guardado(), primeiro)
        self.assertTrue(self.ml.refresh_ainda_vale(codigo_guardado()))

    def test_sem_o_codigo_de_renovacao_a_conta_fica_sem_acesso_guardado(self):
        self.semear()
        with sem_codigo_de_renovacao_no_login(), self.assertLogs(level="ERROR") as registro:
            self.entrar()
        self.assertIn("fluxo Refresh Token", registro.output[0])
        conta = Conta.objects.get(ml_user_id=CONTA)
        self.assertEqual(conta.acesso, "")
        self.assertIsNotNone(conta.sem_acesso_desde)
        self.assertEqual(self.esperar(self.gerar()).estado, PRONTO, "o token de acesso da sessão funciona")
        texto = self.texto(self.abrir("/conta"))
        self.assertIn("Sem acesso guardado<small>o Orzy usa só o acesso desta sessão", texto)
        self.assertNotIn("Acesso guardado com criptografia", texto)

        self.entrar(Navegador())
        codigo = codigo_guardado()
        with sem_codigo_de_renovacao_no_login(), self.assertLogs(level="ERROR"):
            self.entrar(Navegador())
        self.assertEqual(codigo_guardado(), codigo, "a conta que já tinha acesso guardado fica com ele")

    def test_falha_ao_salvar_a_conta_nao_conclui_o_login(self):
        with mock.patch.object(acesso, "guardar", side_effect=DatabaseError("banco fora do ar")), \
                self.assertLogs(level="ERROR"):
            destino = self.ml.autorizar(self.abrir("/entrar")["Location"])
            resposta = self.abrir(destino[len(URL):])
        self.assertEqual(resposta.status_code, 400)
        self.assertIn(login.MENSAGEM_LOGIN_FALHOU, self.texto(resposta))
        self.assertFalse(Conta.objects.exists())
        self.assertEqual(self.abrir("/relatorio").status_code, 302, "sem a conta salva, sem login")


class RenovarTests(SistemaBase):
    def test_renovacoes_ao_mesmo_tempo_saem_uma_de_cada_vez(self):
        # O código de renovação é de uso único: duas renovações com o mesmo código, e a segunda seria recusada.
        self.entrar()
        self.ml.espera_no_token = 0.2  # a resposta do Mercado Livre demora: as renovações se encontram
        resultados, erros = [], []

        def renovar():
            try:
                resultados.append(acesso.renovar(CONTA))
            except Exception as e:
                erros.append(e)
            finally:
                connections.close_all()

        threads = [threading.Thread(target=renovar) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        self.assertEqual(erros, [])
        self.assertEqual(len(self.chamadas_de_token()), 5, "o login e as 4 renovações, nenhuma recusada")
        self.assertEqual(len({r["access_token"] for r in resultados}), 4)
        self.assertFalse(any("refresh_token" in r for r in resultados), "o código de renovação fica só no banco")
        self.assertTrue(self.ml.refresh_ainda_vale(codigo_guardado()))

    def test_o_codigo_novo_e_salvo_antes_de_o_token_sair(self):
        self.entrar()
        guardado = Conta.objects.get(ml_user_id=CONTA).acesso
        with mock.patch.object(Conta, "save", side_effect=DatabaseError("banco fora do ar")):
            with self.assertRaises(DatabaseError):
                acesso.renovar(CONTA)
        self.assertEqual(Conta.objects.get(ml_user_id=CONTA).acesso, guardado)

    def test_erro_que_nao_e_do_acesso_nao_apaga_o_acesso(self):
        self.entrar()
        codigo = codigo_guardado()
        with com_configuracao(client_secret="trocado"), self.assertLogs(level="WARNING"):
            with self.assertRaises(ml_api.ErroLogin) as contexto:
                acesso.renovar(CONTA)
        self.assertNotIsInstance(contexto.exception, acesso.SemAcesso)
        self.assertEqual(str(contexto.exception), acesso.MENSAGEM_NAO_RENOVOU)
        self.assertTrue(self.ml.refresh_ainda_vale(codigo))

        with com_configuracao(chave_acesso=bytes(32)), self.assertLogs(level="ERROR") as registro:
            with self.assertRaises(ml_api.ErroLogin) as contexto:
                acesso.renovar(CONTA)
        self.assertNotIsInstance(contexto.exception, acesso.SemAcesso, "chave trocada não é permissão tirada")
        self.assertIn("ORZY_CHAVE_ACESSO mudou?", registro.output[0])

        self.assertEqual(codigo_guardado(), codigo)
        self.assertIsNone(Conta.objects.get(ml_user_id=CONTA).sem_acesso_desde)
        self.assertTrue(self.sessao(), "a sessão continua")


class ConferenciaTests(SistemaBase):
    def test_renova_quem_nao_renovou_no_dia_e_percebe_quem_tirou_a_permissao(self):
        self.entrar()
        agora = datas.agora()
        Conta.objects.filter(ml_user_id=CONTA).update(acesso_salvo_em=agora - timedelta(hours=21))
        codigo = codigo_guardado()
        criar_conta(444, acesso=cofre.fechar(CHAVE, 444, "TG-renovado-agora-ha-pouco"),
                    acesso_salvo_em=agora - timedelta(hours=1))
        criar_conta(555, acesso=cofre.fechar(CHAVE, 555, "TG-que-o-mercado-livre-recusa"),
                    acesso_salvo_em=agora - timedelta(days=2))
        criar_conta(666, sem_acesso_desde=agora - timedelta(days=3))
        da_555 = self.entrar_sem_mercado_livre({"id": 555, "apelido": "SEM_PERMISSAO"}, Navegador())
        antes = len(self.chamadas_de_token())

        with self.assertLogs(level="INFO"):
            self.assertEqual(acesso.conferir_todos(), (1, 1, 0), "renovadas, perdidas, com erro")
        self.assertEqual(len(self.chamadas_de_token()), antes + 2, "a renovada há pouco e a sem acesso ficam de fora")
        self.assertFalse(self.ml.refresh_ainda_vale(codigo))
        self.assertTrue(self.ml.refresh_ainda_vale(codigo_guardado()))
        self.assertEqual(cofre.abrir(CHAVE, 444, Conta.objects.get(ml_user_id=444).acesso),
                         "TG-renovado-agora-ha-pouco")
        perdida = Conta.objects.get(ml_user_id=555)
        self.assertEqual(perdida.acesso, "")
        self.assertIsNotNone(perdida.sem_acesso_desde)
        self.assertEqual(self.sessao(da_555), {}, "a sessão de quem perdeu o acesso acaba")
        self.assertTrue(self.sessao(), "as outras continuam")

        self.assertEqual(acesso.conferir_todos(), (0, 0, 0), "no mesmo dia não renova de novo")
        # Quem renovou entre a lista da conferência e a vez dele (uma sessão, por exemplo) também não renova de novo.
        self.assertIsNone(acesso.renovar(CONTA, so_se_salvo_antes_de=agora))
        self.assertEqual(len(self.chamadas_de_token()), antes + 2)

    def test_erro_passageiro_tenta_de_novo_no_outro_dia(self):
        self.entrar()
        Conta.objects.filter(ml_user_id=CONTA).update(acesso_salvo_em=datas.agora() - timedelta(days=1))
        codigo = codigo_guardado()
        self.ml.erros_por_rota["/oauth/token"] = 503
        with mock.patch.object(ml_api.time, "sleep"), self.assertLogs(level="WARNING"):
            self.assertEqual(acesso.conferir_todos(), (0, 0, 1))
        self.assertEqual(codigo_guardado(), codigo, "o acesso guardado continua")
        del self.ml.erros_por_rota["/oauth/token"]
        self.assertEqual(acesso.conferir_todos(), (1, 0, 0))

    def test_apaga_quem_esta_sem_acesso_e_sem_conectar_ha_30_dias(self):
        agora = datas.agora()
        mes_passado, semana_passada = agora - timedelta(days=31), agora - timedelta(days=7)
        criar_conta(444, sem_acesso_desde=mes_passado, conectada_em=mes_passado)
        HISTORICO.salvar(444, 30, [LINHA])
        criar_conta(555, sem_acesso_desde=semana_passada, conectada_em=mes_passado)  # perdeu o acesso há pouco
        criar_conta(666, sem_acesso_desde=mes_passado, conectada_em=semana_passada)  # conectou, sem o código
        criar_conta(777, acesso=cofre.fechar(CHAVE, 777, "TG-x"), acesso_salvo_em=agora, conectada_em=mes_passado)
        criar_conta(888, conectada_em=agora - timedelta(days=29, hours=23))
        HISTORICO.salvar(888, 30, [LINHA])
        da_444 = self.entrar_sem_mercado_livre({"id": 444, "apelido": "SAIU"})

        self.assertEqual(acesso.apagar_sem_acesso(), 1)
        self.assertEqual(sorted(Conta.objects.values_list("ml_user_id", flat=True)), [555, 666, 777, 888])
        self.assertEqual(list(RelatorioGuardado.objects.values_list("conta__ml_user_id", flat=True)), [888])
        self.assertEqual(AnuncioGuardado.objects.count(), 1, "os anúncios guardados saem junto, pelo banco")
        self.assertEqual(self.sessao(da_444), {})


class PaginaDaContaTests(SistemaBase):
    def test_mostra_o_que_o_orzy_guarda_da_conta(self):
        self.semear()
        self.entrar()
        self.esperar(self.gerar())
        texto = self.texto(self.abrir("/conta"))
        self.assertIn("<title>Sua conta", texto)
        self.assertIn("<b>LOJA_TESTE</b><small>número 111222333</small>", texto)
        self.assertIn("Acesso guardado com criptografia</p>", texto)
        self.assertRegex(texto, r"<dd>\d{2}/\d{2}/\d{4}<small>último Conectar em \d{2}/\d{2}/\d{4} às \d{2}:\d{2}")
        self.assertRegex(texto, r"Guardado com criptografia<small>atualizado em \d{2}/\d{2}/\d{4} às \d{2}:\d{2}")
        self.assertIn("<dd>1<small>guardados por 12 meses</small>", texto)
        self.assertIn("Se você não conectar de novo em 30 dias, ele apaga também a conta e o histórico.", texto)
        self.assertIn('<form class="hi-apagar-form" method="post" action="/conta/apagar">', texto)
        self.assertIn('href="/conta" title="Sua conta: LOJA_TESTE" aria-current="page"', texto)


class DesconectarTests(SistemaBase):
    def test_apaga_a_conta_o_historico_as_sessoes_e_tira_a_permissao(self):
        self.semear()
        self.entrar()
        outro_navegador = Navegador()
        self.entrar(outro_navegador)
        self.esperar(self.gerar())
        criar_conta(999)
        HISTORICO.salvar(999, 30, [LINHA])
        outra_conta = self.entrar_sem_mercado_livre({"id": 999, "apelido": "OUTRA"}, Navegador())
        codigo = codigo_guardado()

        resposta = self.enviar("/conta/apagar", {"confirmo": "on"})
        self.assertEqual((resposta.status_code, resposta["Location"]), (303, "/conta/apagada"))
        self.assertEqual(str(resposta.cookies["orzy_sessao"]["max-age"]), "0", "o navegador apaga o cookie")
        self.assertEqual(self.ml.permissao_tirada, 1)
        self.assertFalse(self.ml.refresh_ainda_vale(codigo), "o Mercado Livre não aceita mais o acesso do Orzy")
        self.assertEqual(list(Conta.objects.values_list("ml_user_id", flat=True)), [999])
        self.assertEqual(list(RelatorioGuardado.objects.values_list("conta__ml_user_id", flat=True)), [999])
        self.assertEqual(AnuncioGuardado.objects.count(), 1, "só o da outra conta")
        for navegador in (self.client, outro_navegador):
            self.assertEqual(self.sessao(navegador), {}, "a sessão acaba em todos os navegadores da conta")
        self.assertTrue(self.sessao(outra_conta), "a sessão de outra conta continua")

        texto = self.texto(self.abrir("/conta/apagada"))
        self.assertIn('<h1 class="er-titulo">Conta apagada</h1>', texto)
        self.assertIn("Alguma dúvida? Escreva para", texto)
        self.assertIn(APAGADA, texto)
        self.assertEqual(self.abrir("/relatorio").status_code, 302)

    def test_sem_o_token_da_sessao_tira_a_permissao_com_o_acesso_guardado(self):
        self.entrar()
        self.ml.revogar_access_tokens()
        resposta = self.enviar("/conta/apagar", {"confirmo": "on"})
        self.assertEqual(resposta["Location"], "/conta/apagada")
        self.assertEqual(self.ml.permissao_tirada, 1)
        self.assertEqual(len(self.chamadas_de_token()), 2, "o login e uma renovação para tirar a permissão")

    def test_se_o_mercado_livre_nao_confirmar_apaga_do_mesmo_jeito(self):
        self.semear()
        self.entrar()
        self.esperar(self.gerar())
        self.ml.erros_por_rota[f"/users/{CONTA}/applications"] = 403
        with self.assertLogs(level="WARNING") as registro:
            resposta = self.enviar("/conta/apagar", {"confirmo": "on"})
        self.assertIn("Não consegui tirar a permissão do Orzy no Mercado Livre", "\n".join(registro.output))
        self.assertEqual(resposta["Location"], "/conta/apagada?mercado-livre=nao")
        self.assertFalse(Conta.objects.exists())
        self.assertFalse(RelatorioGuardado.objects.exists())
        self.assertEqual(self.sessao(), {})
        self.assertIn(APAGADA_SEM_O_MERCADO_LIVRE, self.texto(self.abrir("/conta/apagada?mercado-livre=nao")))

    def test_pede_a_confirmacao_e_o_codigo_do_formulario(self):
        self.entrar()
        resposta = self.enviar("/conta/apagar")
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("Confirme que quer desconectar e apagar tudo.", self.texto(resposta))
        for resposta in (self.enviar("/conta/apagar", {"confirmo": "on"}, com_codigo=False),
                         self.enviar("/conta/apagar", {"confirmo": "on"}, origem="https://site-estranho.example")):
            self.assertEqual(resposta.status_code, 403)
        self.assertEqual(self.abrir("/conta/apagar").status_code, 404, "só pelo formulário")
        self.assertTrue(Conta.objects.filter(ml_user_id=CONTA).exists())
        self.assertEqual(self.ml.permissao_tirada, 0)
        self.assertTrue(self.sessao(), "a sessão continua")
