"""Regras sem página: configuração, sessões, comparação, busca, contagens, datas e os textos que as telas mostram."""

from datetime import date, datetime, timezone
from unittest import mock

import ml_api
from contas import login, sessoes
from django.http import QueryDict
from django.test import RequestFactory, SimpleTestCase
from orzy import configuracao, contexto
from relatorios import busca, comparacao, contagens, datas, formatos

ENV = {"ORZY_ML_CLIENT_ID": "1", "ORZY_ML_CLIENT_SECRET": "s", "ORZY_URL_BASE": "https://orzy.test",
       "ORZY_BANCO_URL": "postgresql://orzy:senha@127.0.0.1:5432/orzy"}


class ConfiguracaoTests(SimpleTestCase):
    def test_avisa_quais_variaveis_faltam(self):
        with self.assertRaises(configuracao.ErroConfiguracao) as contexto_:
            configuracao.carregar({"ORZY_ML_CLIENT_ID": "1"})
        for nome in ("ORZY_ML_CLIENT_SECRET", "ORZY_URL_BASE", "ORZY_BANCO_URL"):
            self.assertIn(nome, str(contexto_.exception))

    def test_exige_https_fora_do_computador(self):
        with self.assertRaises(configuracao.ErroConfiguracao):
            configuracao.carregar(dict(ENV, ORZY_URL_BASE="http://exemplo.com"))
        local = configuracao.carregar(dict(ENV, ORZY_URL_BASE="http://127.0.0.1:8000"))
        self.assertFalse(local.seguro, "no computador, o cookie vai sem Secure")

    def test_valores_padrao(self):
        config = configuracao.carregar(dict(ENV, ORZY_URL_BASE="https://orzy.test/"))
        self.assertEqual(config.url_base, "https://orzy.test")
        self.assertEqual(config.redirect_uri, "https://orzy.test/retorno")
        self.assertEqual(config.origem, "https://orzy.test")
        self.assertEqual(config.host, "orzy.test")
        self.assertEqual((config.max_anuncios, config.horas_sessao, config.contas_admin), (300, 8, frozenset()))
        self.assertTrue(config.seguro)

    def test_le_o_endereco_do_banco_sem_mostrar_a_senha(self):
        url = "postgresql://orzy:s%40nha@db.exemplo.com:6543/orzy?sslmode=require"
        config = configuracao.carregar(dict(ENV, ORZY_BANCO_URL=url))
        self.assertEqual(config.banco, {
            "ENGINE": "django.db.backends.postgresql", "NAME": "orzy", "USER": "orzy", "PASSWORD": "s@nha",
            "HOST": "db.exemplo.com", "PORT": "6543", "OPTIONS": {"sslmode": "require"}})
        self.assertNotIn("s@nha", repr(config), "a senha do banco não aparece no registro")
        for errado in ("mysql://u:s@h/b", "postgresql://u:s@h", "postgresql://u:s@h:porta/b", "orzy"):
            with self.assertRaises(configuracao.ErroConfiguracao, msg=errado):
                configuracao.carregar(dict(ENV, ORZY_BANCO_URL=errado))

    def test_numeros_dentro_dos_limites(self):
        self.assertEqual(configuracao.carregar(dict(ENV, ORZY_HORAS_SESSAO="4")).horas_sessao, 4)
        self.assertEqual(configuracao.carregar(dict(ENV, ORZY_MAX_ANUNCIOS="50")).max_anuncios, 50)
        # A Política de Privacidade promete no máximo 8 horas.
        for nome, errado in (("ORZY_HORAS_SESSAO", "9"), ("ORZY_HORAS_SESSAO", "0"), ("ORZY_MAX_ANUNCIOS", "abc"),
                             ("ORZY_MAX_ANUNCIOS", "１２")):
            with self.assertRaises(configuracao.ErroConfiguracao) as contexto_:
                configuracao.carregar(dict(ENV, **{nome: errado}))
            self.assertIn(nome, str(contexto_.exception))

    def test_contas_que_abrem_a_pagina_de_contagens(self):
        config = configuracao.carregar(dict(ENV, ORZY_CONTAS_ADMIN=" 123, 456 ,"))
        self.assertEqual(config.contas_admin, frozenset({123, 456}))
        for errado in ("LOJA_TESTE", "123;456", "１２３"):
            with self.assertRaises(configuracao.ErroConfiguracao) as contexto_:
                configuracao.carregar(dict(ENV, ORZY_CONTAS_ADMIN=errado))
            self.assertIn("ORZY_CONTAS_ADMIN", str(contexto_.exception))


class SessoesTests(SimpleTestCase):
    def setUp(self):
        self.relogio = [1000.0]

    def novas(self, **extra):
        return sessoes.Sessoes(horas=8, agora=lambda: self.relogio[0], **extra)

    def logada(self):
        return {"cliente": object(), "login_em": self.relogio[0]}

    def test_sessao_com_login_acaba_no_prazo_contado_do_login_mesmo_em_uso(self):
        # A Política de Privacidade promete: no máximo 8 horas depois de entrar. Usar o site não estica o prazo.
        guardadas = self.novas()
        guardadas.criar("antes", {})  # clicou em Conectar
        self.relogio[0] += 60  # um minuto no Mercado Livre
        guardadas.encerrar("antes")  # o login troca o código da sessão
        guardadas.criar("depois", self.logada())
        for _ in range(7):
            self.relogio[0] += 3600  # usada a cada hora
            self.assertIsNotNone(guardadas.obter("depois"))
        self.relogio[0] += 3599
        self.assertIsNotNone(guardadas.obter("depois"), "1 segundo antes das 8 horas")
        self.relogio[0] += 2
        self.assertIsNone(guardadas.obter("depois"), "8 horas depois do login, mesmo usada a cada hora")

    def test_limpeza_apaga_a_sessao_vencida_sem_pedido_e_antes_do_prazo(self):
        # Sem ninguém usando o site, a sessão também sai da memória: o servidor chama limpar() a cada minuto.
        guardadas = self.novas()
        guardadas.criar("s", self.logada())
        self.relogio[0] += 8 * 3600 - 61
        guardadas.limpar(antecedencia=60)
        self.assertIn("s", guardadas._dados, "vence daqui a 61 segundos: fica para a próxima limpeza")
        self.relogio[0] += 2
        guardadas.limpar(antecedencia=60)
        self.assertNotIn("s", guardadas._dados, "venceria antes da próxima limpeza: sai agora")

    def test_sessao_sem_login_some_em_15_minutos_e_tem_limite(self):
        guardadas = self.novas(max_pendentes=3)
        guardadas.criar("logada", self.logada())
        guardadas.criar("pendente", {})
        self.relogio[0] += 15 * 60 + 1
        self.assertIsNone(guardadas.obter("pendente"), "quem não voltou do Mercado Livre sai em 15 minutos")
        self.assertIsNotNone(guardadas.obter("logada"))

        for n in range(3):
            self.relogio[0] += 1
            guardadas.criar(f"p{n}", {})
        self.relogio[0] += 1
        guardadas.criar("nova", {})
        self.assertNotIn("p0", guardadas._dados, "no limite, sai a sessão sem login mais antiga")
        for chave in ("p1", "p2", "nova", "logada"):
            self.assertIn(chave, guardadas._dados)

    def test_sessao_que_acabou_nao_volta(self):
        guardadas = self.novas()
        self.assertTrue(guardadas.criar("a", {}))
        self.assertFalse(guardadas.criar("a", {}), "código repetido não troca a sessão de ninguém")
        guardadas.encerrar("a")  # Sair em outra aba
        guardadas.guardar("a", self.logada())  # o fim do pedido que estava no meio
        self.assertNotIn("a", guardadas._dados)


class ComparacaoTests(SimpleTestCase):
    def test_diz_o_que_mudou_em_cada_anuncio(self):
        def anuncio(id_, titulo, visitas, vendas, situacao):
            return {"id": id_, "titulo": titulo, "visitas": visitas, "vendas": vendas, "situacao": situacao,
                    "pontos": 0}
        anterior = {"id": 1, "criado_em": datetime(2026, 10, 1, 12, tzinfo=timezone.utc), "anuncios": [
            anuncio("MLB1", "Fone", 100, 0, "VISITA SEM VENDA"),
            anuncio("MLB2", "Cabo", 10, 1, "VENDE, MAS POUCO VISTO"),
            anuncio("MLB3", "Caixa", None, None, "SEM DADOS"),
            anuncio("MLB4", "Capa", 5, 0, "POUCA VISITA")]}
        atual = {"id": 2, "criado_em": datetime(2026, 10, 8, 12, tzinfo=timezone.utc), "anuncios": [
            anuncio("MLB1", "Fone Bluetooth Sem Fio", 150, 3, "VENDENDO BEM"),
            anuncio("MLB2", "Cabo", 12, 1, "VENDE, MAS POUCO VISTO"),
            anuncio("MLB3", "Caixa", 40, 0, "VISITA SEM VENDA"),
            anuncio("MLB5", "Suporte", 7, 0, "POUCA VISITA")]}
        mudou = comparacao.comparar(anterior, atual)
        self.assertEqual([a["id"] for a in mudou["mudaram_de_situacao"]], ["MLB1", "MLB3"])
        self.assertEqual(mudou["titulos_mudaram"], 1)
        self.assertEqual([a["id"] for a in mudou["novos"]], ["MLB5"])
        self.assertEqual([a["id"] for a in mudou["sairam"]], ["MLB4"])
        self.assertEqual(mudou["visitas"], (115, 209), "anúncio sem dados não entra na soma")
        self.assertEqual(mudou["vendas"], (1, 4))
        self.assertEqual(mudou["antes"]["MLB1"]["titulo"], "Fone")
        self.assertEqual(mudou["anterior"], {"id": 1, "criado_em": anterior["criado_em"]})


class BuscaTests(SimpleTestCase):
    def test_le_a_busca_e_a_situacao_do_endereco(self):
        self.assertEqual(busca.ler(QueryDict("busca=+C%C3%A2mera++Sony+&situacao=VENDENDO+BEM")),
                         ("Câmera Sony", "VENDENDO BEM"))
        self.assertEqual(busca.ler(QueryDict("situacao=QUALQUER+COISA")), ("", ""),
                         "situação desconhecida vale como todas")
        self.assertEqual(busca.ler(QueryDict("")), ("", ""))
        self.assertEqual(len(busca.ler(QueryDict("busca=" + "a" * 500))[0]), busca.MAX_BUSCA)

    def test_acha_sem_acento_sem_maiuscula_e_em_qualquer_ordem(self):
        anuncios = [{"titulo": "Câmera Digital Sony", "situacao": "VENDENDO BEM"},
                    {"titulo": "Capa para CÂMERA", "situacao": "POUCA VISITA"},
                    {"titulo": "", "situacao": "SEM DADOS"}]

        def titulos(texto, situacao=""):
            return [a["titulo"] for a in busca.filtrar(anuncios, texto, situacao)]

        self.assertEqual(titulos("camera"), ["Câmera Digital Sony", "Capa para CÂMERA"])
        self.assertEqual(titulos("sony câmera"), ["Câmera Digital Sony"], "as palavras em qualquer ordem")
        self.assertEqual(titulos("camera", "POUCA VISITA"), ["Capa para CÂMERA"])
        self.assertEqual(titulos("", "SEM DADOS"), [""])
        self.assertEqual(titulos(""), [a["titulo"] for a in anuncios])


class ContagensTests(SimpleTestCase):
    def test_dia_no_horario_de_brasilia(self):
        self.assertEqual(datas.hoje(datetime(2026, 10, 15, 2, 59, tzinfo=timezone.utc)), date(2026, 10, 14))
        self.assertEqual(datas.hoje(datetime(2026, 10, 15, 3, 0, tzinfo=timezone.utc)), date(2026, 10, 15))

    def test_sem_nada_para_contar_nao_grava(self):
        historico = mock.Mock()
        contagens.contar(historico)
        historico.somar_contagens.assert_not_called()

    def test_falha_ao_contar_fica_so_no_registro(self):
        historico = mock.Mock()
        historico.somar_contagens.side_effect = RuntimeError("banco fora do ar")
        with self.assertLogs(level="ERROR") as registro:
            contagens.contar(historico, logins=1)
        self.assertIn("contagem do beta", registro.output[0])

    def test_resumo_da_pagina(self):
        historico = mock.Mock()
        historico.ler_contagens.return_value = {
            date(2026, 10, 14): {"logins": 2, "relatorios_prontos": 3, "erros_mercado_livre": 1},
            date(2026, 10, 15): {"logins": 1, "anuncios_lidos": 40}}
        historico.ultimo_total_de_cada_conta.return_value = [1, 2, 6]
        dados = contagens.resumo(historico, 6)
        self.assertEqual(dados["desde"], date(2026, 10, 14))
        self.assertEqual(dict(dados["totais"])["Logins"], 3)
        self.assertEqual(dados["sem_erro"], {"prontos": 3, "feitos": 4, "pct": 75})
        self.assertEqual([dia for dia, _ in dados["dias"]], [date(2026, 10, 15), date(2026, 10, 14)],
                         "o dia mais recente primeiro")
        self.assertEqual(dados["dias"][0][1], [1, 0, 0, 0, 40], "um número por coluna, na ordem da página")
        self.assertEqual((dados["contas"], dados["anuncios"]),
                         (3, {"menor": 1, "media": 3, "maior": 6, "no_limite": 1}))


class ClienteDaSessaoTests(SimpleTestCase):
    def test_nao_renova_o_login_sozinho(self):
        cliente = login.ClienteDaSessao({"client_id": "1", "client_secret": "s", "redirect_uri": "x"},
                                        {"access_token": "APP_USR-x", "expira_em": 0})
        with self.assertRaises(ml_api.ErroLogin) as contexto_:
            cliente._access_token()
        self.assertIn("Clique em Conectar de novo", str(contexto_.exception))


class FormatosTests(SimpleTestCase):
    def test_numeros_em_portugues(self):
        self.assertEqual(formatos.milhar(2417), "2.417")
        self.assertEqual(formatos.milhar(None), "?")
        self.assertEqual(formatos.decimal(82.13), "82,1")
        self.assertEqual(formatos.decimal(1234.5, 2), "1.234,50")
        self.assertEqual(formatos.dinheiro(59.9), "59,90")

    def test_datas_no_horario_de_brasilia(self):
        momento = datetime(2026, 10, 15, 2, 30, tzinfo=timezone.utc)  # ainda é 14/10 em Brasília
        self.assertEqual(formatos.data_hora(momento), "14/10/2026 às 23:30")
        self.assertEqual(formatos.dia_e_mes(momento), "14 out")
        with mock.patch.object(datas, "hoje", return_value=date(2026, 10, 15)):
            self.assertEqual(formatos.quando(datetime(2026, 10, 15, 23, 0, tzinfo=timezone.utc)), "hoje, 20:00")
            self.assertEqual(formatos.quando(momento), "14/10, 23:30")

    def test_diferenca_com_sinal_de_menos(self):
        self.assertEqual(formatos.diferenca(100, 84), {"texto": "−16", "classe": "desce"})
        self.assertEqual(formatos.diferenca(1000, 2500), {"texto": "+1.500", "classe": "sobe"})
        self.assertIsNone(formatos.diferenca(5, 5))
        self.assertIsNone(formatos.diferenca(None, 3))

    def test_situacao_com_a_prioridade(self):
        self.assertEqual(formatos.situacao("VISITA SEM VENDA"), {
            "nome": "Visita sem venda", "classe": "vsv", "prioridade": 3, "nome_prioridade": "alta",
            "barras": [True, True, True]})
        self.assertEqual(formatos.situacao("VENDENDO BEM")["barras"], [True, False, False])
        self.assertEqual(formatos.situacao("SEM DADOS")["barras"], [], "sem dados, sem prioridade")
        self.assertEqual(formatos.area("titulo_curto"), "Título")
        self.assertEqual(formatos.area("fotos:poucas"), "Fotos")
        self.assertEqual(formatos.area("outra_coisa"), "Anúncio")

    def test_barra_de_situacoes(self):
        fatias = formatos.barra({"VISITA SEM VENDA": 1, "POUCA VISITA": 3, "SEM DADOS": 0}, 4)
        self.assertEqual(fatias, [{"classe": "vsv", "x": "0.00", "largura": "24.20"},
                                  {"classe": "pv", "x": "25.00", "largura": "74.20"}])


class ContextoTests(SimpleTestCase):
    def pagina(self, caminho, sessao=None):
        pedido = RequestFactory().get(caminho)
        pedido.session = sessao or {}
        return contexto.orzy(pedido)

    def test_iniciais_do_apelido(self):
        for apelido, iniciais in (("LOJA_EXEMPLO", "LE"), ("joaosilva", "JO"), ("Maria Clara", "MC"), ("", ""),
                                  ("___", "")):
            self.assertEqual(contexto._iniciais(apelido), iniciais, apelido)
        dados = self.pagina("/relatorio", {"cliente": object(), "usuario": {"id": 1, "apelido": "LOJA_EXEMPLO"}})
        self.assertEqual((dados["conta"]["apelido"], dados["conta"]["iniciais"]), ("LOJA_EXEMPLO", "LE"))
        self.assertEqual(self.pagina("/")["conta"]["iniciais"], "", "sem login, sem iniciais")

    def test_aba_marcada_no_topo(self):
        for caminho, aba in (("/relatorio", "relatorio"), ("/relatorio/abc", "relatorio"), ("/historico", "historico"),
                             ("/historico/5", "historico"), ("/contagens", "")):
            self.assertEqual(self.pagina(caminho)["aba"], aba, caminho)
        self.assertEqual(self.pagina("/")["meses_de_historico"], 12)
