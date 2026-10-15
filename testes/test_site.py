"""Testes do site (web/) contra o Mercado Livre simulado (ml_simulado.py).

Rodar, na pasta principal do Orzy:
    python -m unittest discover -s testes -v

Nada aqui fala com o Mercado Livre de verdade. O histórico dos testes fica numa pasta temporária.
"""

import http.client
import socket
import sqlite3
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

PASTA_TESTES = Path(__file__).resolve().parent
PASTA_RAIZ = PASTA_TESTES.parent
sys.path.insert(0, str(PASTA_RAIZ))
sys.path.insert(0, str(PASTA_TESTES))
sys.path.insert(0, str(PASTA_RAIZ / "painel-ml"))

import analise  # noqa: E402
import ml_api  # noqa: E402
from ml_simulado import MLSimulado, performance  # noqa: E402
from web import app, comparacao, configuracao, login, relatorios, servidor, sessoes  # noqa: E402
from web.historico import Historico  # noqa: E402

URL = "https://orzy.test"
CLIENT_ID = "1234567890"
SECRET = "segredo-de-teste"
TITULO_BOM = "Fone de Ouvido Bluetooth Sem Fio Marca Teste Modelo X1 Preto"


def _cab(cabecalhos, nome):
    return next((valor for n, valor in cabecalhos if n == nome), None)


def _id_da_sessao(cookie):
    return cookie.split("=", 1)[1]


def configuracao_de_teste(banco, **extra):
    base = dict(client_id=CLIENT_ID, client_secret=SECRET, url_base=URL, banco=str(banco),
                host="127.0.0.1", porta=0, max_anuncios=300, horas_sessao=8)
    base.update(extra)
    return configuracao.Configuracao(**base)


class SiteBase(unittest.TestCase):
    def setUp(self):
        self.ml = MLSimulado(client_id=CLIENT_ID, client_secret=SECRET, redirect_uri=URL + "/retorno",
                             user_id=111222333, nickname="LOJA_TESTE")
        base = self.ml.iniciar()
        self.addCleanup(self.ml.parar)

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.pasta = Path(temp.name)

        # Aponta o site para o simulado e para uma pasta temporária. Nada pode ser gravado na pasta do painel.
        for trocar in [
            mock.patch.object(ml_api, "API_BASE", base),
            mock.patch.object(ml_api, "AUTH_URL", base + "/authorization"),
            mock.patch.object(ml_api, "ARQ_CONFIG", self.pasta / "config.json"),
            mock.patch.object(ml_api, "ARQ_TOKENS", self.pasta / "tokens.json"),
        ]:
            trocar.start()
            self.addCleanup(trocar.stop)

        # Os textos legais saem de uma pasta temporária: os testes não dependem de docs/legal/.
        self.pasta_legal = self.pasta / "legal"
        self.site = app.Site(configuracao_de_teste(self.pasta / "orzy.db"), pasta_legal=self.pasta_legal)

    def semear(self):
        self.ml.adicionar_item("MLB1000000001", TITULO_BOM, preco=79.9, estoque=10, visitas=0)
        self.ml.adicionar_item("MLB1000000002", "<script>alert(1)</script> Caixa de som", visitas=120)
        self.ml.adicionar_pedido("MLB1000000002", quantidade=2, dias_atras=3)
        self.ml.qualidade["MLB1000000002"] = performance("MLB1000000002", 88, "Good", "Profissional")

    def entrar(self):
        """O login inteiro: /entrar, o clique em Permitir no simulado e o retorno. Devolve o cookie da sessão."""
        status, cabecalhos, _ = self.site.tratar("GET", "/entrar", {})
        self.assertEqual(status, 302)
        cookie = _cab(cabecalhos, "Set-Cookie").split(";")[0]
        endereco = self.ml.autorizar(_cab(cabecalhos, "Location"))
        status, cabecalhos, _ = self.site.tratar("GET", endereco[len(URL):], {"Cookie": cookie})
        self.assertEqual(status, 302, "o retorno deveria levar para /relatorio")
        self.assertEqual(_cab(cabecalhos, "Location"), "/relatorio")
        return _cab(cabecalhos, "Set-Cookie").split(";")[0]  # o login troca o código da sessão

    def gerar(self, cookie, dias=30):
        status, cabecalhos, _ = self.site.tratar("POST", "/relatorio/gerar",
                                                 {"Cookie": cookie, "Origin": URL}, f"dias={dias}".encode())
        self.assertEqual(status, 303)
        return _cab(cabecalhos, "Location").rsplit("/", 1)[1]

    def esperar(self, cookie, relatorio_id):
        relatorio = self.site.sessoes.obter(_id_da_sessao(cookie)).relatorios[relatorio_id]
        relatorio.thread.join(timeout=30)
        self.assertIsNotNone(relatorio.thread)
        self.assertFalse(relatorio.thread.is_alive(), "o relatório demorou demais")
        return relatorio

    def pedir(self, metodo, caminho, cookie=None, corpo=b"", origem=URL):
        cabecalhos = {"Origin": origem} if origem else {}
        if cookie:
            cabecalhos["Cookie"] = cookie
        return self.site.tratar(metodo, caminho, cabecalhos, corpo)

    def chamadas_de_token(self):
        return [c for c in self.ml.chamadas if c[0] == "POST" and c[1] == "/oauth/token"]


class ConfiguracaoTests(unittest.TestCase):
    def test_avisa_quais_variaveis_faltam(self):
        with self.assertRaises(configuracao.ErroConfiguracao) as contexto:
            configuracao.carregar({})
        self.assertIn("ORZY_ML_CLIENT_SECRET", str(contexto.exception))

    def test_exige_https_fora_do_computador(self):
        env = {"ORZY_ML_CLIENT_ID": "1", "ORZY_ML_CLIENT_SECRET": "s", "ORZY_URL_BASE": "http://exemplo.com"}
        with self.assertRaises(configuracao.ErroConfiguracao):
            configuracao.carregar(env)

    def test_valores_padrao_e_porta_da_hospedagem(self):
        env = {"ORZY_ML_CLIENT_ID": "1", "ORZY_ML_CLIENT_SECRET": "s", "ORZY_URL_BASE": "https://orzy.test/",
               "PORT": "9000"}
        config = configuracao.carregar(env)
        self.assertEqual(config.url_base, "https://orzy.test")
        self.assertEqual(config.redirect_uri, "https://orzy.test/retorno")
        self.assertEqual(config.origem, "https://orzy.test")
        self.assertEqual(config.porta, 9000)
        self.assertEqual(config.max_anuncios, 300)
        self.assertTrue(config.seguro)


class SessoesTests(unittest.TestCase):
    def test_sessao_some_depois_do_prazo_sem_uso(self):
        relogio = [1000.0]
        guardadas = sessoes.Sessoes(horas=1, agora=lambda: relogio[0])
        sessao = guardadas.criar()
        sessao.cliente = object()  # já entrou com o Mercado Livre
        relogio[0] += 3000
        self.assertIsNotNone(guardadas.obter(sessao.id))  # o uso renova o prazo
        relogio[0] += 3000
        self.assertIsNotNone(guardadas.obter(sessao.id))
        relogio[0] += 3601 * 2
        self.assertIsNone(guardadas.obter(sessao.id))

    def test_sessao_sem_login_some_em_15_minutos_e_tem_limite(self):
        relogio = [1000.0]
        guardadas = sessoes.Sessoes(horas=8, agora=lambda: relogio[0], max_pendentes=3)
        logada = guardadas.criar()
        logada.cliente = object()
        pendente = guardadas.criar()
        relogio[0] += 15 * 60 + 1
        self.assertIsNone(guardadas.obter(pendente.id), "quem não voltou do Mercado Livre sai em 15 minutos")
        self.assertIsNotNone(guardadas.obter(logada.id))

        primeiras = []
        for _ in range(3):
            relogio[0] += 1
            primeiras.append(guardadas.criar())
        relogio[0] += 1
        nova = guardadas.criar()
        self.assertNotIn(primeiras[0].id, guardadas._dados, "no limite, sai a sessão sem login mais antiga")
        for sessao in (*primeiras[1:], nova, logada):
            self.assertIn(sessao.id, guardadas._dados)


class HistoricoTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.caminho = Path(temp.name) / "orzy.db"
        self.historico = Historico(str(self.caminho))
        self.linhas = [
            {"id": "MLB1", "titulo": "Anúncio A", "visitas": 5, "vendas": 0, "situacao": "VISITA SEM VENDA",
             "pontos": 3},
            {"id": "MLB2", "titulo": "Anúncio B", "visitas": None, "vendas": None, "situacao": "POUCA VISITA",
             "pontos": 0},
        ]

    def test_salva_lista_ve_e_apaga_so_da_conta_pedida(self):
        id_ = self.historico.salvar(111, 30, self.linhas)
        self.historico.salvar(222, 30, self.linhas)
        lista = self.historico.listar(111)
        self.assertEqual([r["id"] for r in lista], [id_])
        self.assertEqual(lista[0]["resumo"]["VISITA SEM VENDA"], 1)
        dados = self.historico.ver(111, id_)
        self.assertEqual([a["id"] for a in dados["anuncios"]], ["MLB1", "MLB2"])
        self.assertIsNone(self.historico.ver(222, id_), "outra conta não pode ver o relatório")
        self.assertEqual(self.historico.apagar(111), 1)
        self.assertEqual(self.historico.listar(111), [])
        self.assertEqual(len(self.historico.listar(222)), 1)

    def test_apaga_relatorios_mais_velhos_que_o_prazo(self):
        self.historico.salvar(111, 30, self.linhas)
        con = sqlite3.connect(self.caminho)
        with con:
            con.execute("UPDATE relatorios SET criado_em = '2000-01-01T00:00:00+00:00'")
        con.close()
        self.historico.salvar(111, 30, self.linhas)
        self.assertEqual(self.historico.apagar_antigos(365), 1)
        self.assertEqual(len(self.historico.listar(111)), 1)

    def test_anterior_e_o_ultimo_da_mesma_conta_e_do_mesmo_periodo(self):
        primeiro = self.historico.salvar(111, 30, self.linhas)
        self.historico.salvar(111, 60, self.linhas)  # outro período: os números não são comparáveis
        self.historico.salvar(222, 30, self.linhas)  # outra conta: nunca
        segundo = self.historico.salvar(111, 30, self.linhas)
        terceiro = self.historico.salvar(111, 30, self.linhas)
        self.assertIsNone(self.historico.id_do_anterior(111, primeiro))
        self.assertEqual(self.historico.id_do_anterior(111, segundo), primeiro)
        self.assertEqual(self.historico.id_do_anterior(111, terceiro), segundo)
        self.assertIsNone(self.historico.id_do_anterior(222, terceiro), "o relatório pedido não é da conta 222")


class ComparacaoTests(unittest.TestCase):
    def test_diz_o_que_mudou_em_cada_anuncio(self):
        def anuncio(id_, titulo, visitas, vendas, situacao):
            return {"id": id_, "titulo": titulo, "visitas": visitas, "vendas": vendas, "situacao": situacao,
                    "pontos": 0}
        anterior = {"id": 1, "criado_em": "2026-10-01T12:00:00+00:00", "anuncios": [
            anuncio("MLB1", "Fone", 100, 0, "VISITA SEM VENDA"),
            anuncio("MLB2", "Cabo", 10, 1, "VENDE, MAS POUCO VISTO"),
            anuncio("MLB3", "Caixa", None, None, "SEM DADOS"),
            anuncio("MLB4", "Capa", 5, 0, "POUCA VISITA")]}
        atual = {"id": 2, "criado_em": "2026-10-08T12:00:00+00:00", "anuncios": [
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
        self.assertEqual(mudou["anterior"], {"id": 1, "criado_em": "2026-10-01T12:00:00+00:00"})


class ClienteDaSessaoTests(unittest.TestCase):
    def test_nao_renova_o_login_sozinho(self):
        cliente = login.ClienteDaSessao({"client_id": "1", "client_secret": "s", "redirect_uri": "x"},
                                        {"access_token": "APP_USR-x", "expira_em": 0})
        with self.assertRaises(ml_api.ErroLogin) as contexto:
            cliente._access_token()
        self.assertIn("Clique em Conectar de novo", str(contexto.exception))


class LoginTests(SiteBase):
    def test_entrar_leva_ao_mercado_livre_com_pkce_e_estado(self):
        status, cabecalhos, _ = self.pedir("GET", "/entrar", origem=None)
        self.assertEqual(status, 302)
        destino = _cab(cabecalhos, "Location")
        self.assertTrue(destino.startswith(ml_api.AUTH_URL))
        for pedaco in ("code_challenge_method=S256", "state=", "redirect_uri=https%3A%2F%2Forzy.test%2Fretorno"):
            self.assertIn(pedaco, destino)
        cookie = _cab(cabecalhos, "Set-Cookie")
        for atributo in ("HttpOnly", "SameSite=Lax", "Secure", "Max-Age=28800", "Path=/"):
            self.assertIn(atributo, cookie)

    def test_retorno_com_estado_trocado_nao_troca_o_codigo(self):
        status, cabecalhos, _ = self.pedir("GET", "/entrar", origem=None)
        cookie = _cab(cabecalhos, "Set-Cookie").split(";")[0]
        status, _, dados = self.pedir("GET", "/retorno?code=TG-falso&state=outro", cookie=cookie, origem=None)
        self.assertEqual(status, 400)
        self.assertIn("não é válido".encode("utf-8"), dados)
        self.assertEqual(self.chamadas_de_token(), [])

    def test_login_guarda_o_token_so_na_sessao(self):
        cookie = self.entrar()
        sessao = self.site.sessoes.obter(_id_da_sessao(cookie))
        self.assertEqual(sessao.usuario, {"id": 111222333, "apelido": "LOJA_TESTE"})
        self.assertNotIn("refresh_token", sessao.cliente.tokens)
        self.assertFalse(ml_api.ARQ_TOKENS.exists(), "o login do site não pode ir para o disco")
        self.assertFalse(ml_api.ARQ_CONFIG.exists())
        self.assertNotIn(sessao.cliente.tokens["access_token"], cookie)

    def test_login_troca_o_codigo_da_sessao(self):
        status, cabecalhos, _ = self.pedir("GET", "/entrar", origem=None)
        antes = _cab(cabecalhos, "Set-Cookie").split(";")[0]
        endereco = self.ml.autorizar(_cab(cabecalhos, "Location"))
        status, cabecalhos, _ = self.pedir("GET", endereco[len(URL):], cookie=antes, origem=None)
        self.assertEqual((status, _cab(cabecalhos, "Location")), (302, "/relatorio"))
        novo_cookie = _cab(cabecalhos, "Set-Cookie")
        for atributo in ("HttpOnly", "SameSite=Lax", "Secure", "Max-Age=28800", "Path=/"):
            self.assertIn(atributo, novo_cookie)
        depois = novo_cookie.split(";")[0]
        self.assertNotEqual(antes, depois)
        self.assertEqual(self.pedir("GET", "/relatorio", cookie=antes)[0], 302, "o código de antes do login não entra")
        self.assertEqual(self.pedir("GET", "/relatorio", cookie=depois)[0], 200)

    def test_sem_login_nao_ve_relatorio(self):
        status, cabecalhos, _ = self.pedir("GET", "/relatorio")
        self.assertEqual((status, _cab(cabecalhos, "Location")), (302, "/"))

    def test_sair_encerra_a_sessao(self):
        cookie = self.entrar()
        status, cabecalhos, _ = self.pedir("POST", "/sair", cookie=cookie)
        self.assertEqual((status, _cab(cabecalhos, "Location")), (302, "/"))
        self.assertIsNone(self.site.sessoes.obter(_id_da_sessao(cookie)))


class RelatorioTests(SiteBase):
    def test_gera_mostra_resultado_com_escape_e_baixa_csv(self):
        self.semear()
        cookie = self.entrar()
        relatorio_id = self.gerar(cookie)
        relatorio = self.esperar(cookie, relatorio_id)
        self.assertEqual(relatorio.estado, relatorios.PRONTO)

        status, cabecalhos, pagina = self.pedir("GET", f"/relatorio/{relatorio_id}", cookie=cookie)
        self.assertEqual(status, 200)
        texto = pagina.decode("utf-8")
        self.assertIn("Comece por estes", texto)
        self.assertIn("Caixa de som", texto)
        self.assertNotIn("<script>alert(1)</script>", texto, "título do Mercado Livre tem que sair escapado")
        self.assertIn("&lt;script&gt;", texto)
        # Os termos do Mercado Livre (5.3) pedem que o aplicativo diga quando os dados foram atualizados.
        self.assertRegex(texto, r"Dados buscados no Mercado Livre em \d{2}/\d{2}/\d{4} às \d{2}:\d{2}")
        # A hora é a de Brasília: 02h30 em UTC ainda é o dia anterior aqui.
        relatorio.gerado_em = datetime(2026, 10, 15, 2, 30, tzinfo=timezone.utc)
        texto = self.pedir("GET", f"/relatorio/{relatorio_id}", cookie=cookie)[2].decode("utf-8")
        self.assertIn("Dados buscados no Mercado Livre em 14/10/2026 às 23:30 (horário de Brasília)", texto)

        status, cabecalhos, csv_bytes = self.pedir("GET", f"/relatorio/{relatorio_id}/csv", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertTrue(csv_bytes.startswith("﻿".encode("utf-8")), "o CSV precisa do BOM para o Excel")
        csv_texto = csv_bytes.decode("utf-8-sig")
        cabecalho = csv_texto.splitlines()[0]
        self.assertTrue(cabecalho.startswith("id;titulo;preco;estoque;visitas_30d;vendas_30d"))
        self.assertIn("MLB1000000002", csv_texto)
        self.assertEqual(_cab(cabecalhos, "Content-Type"), "text/csv; charset=utf-8")

        guardado = self.site.historico.listar(111222333)
        self.assertEqual(len(guardado), 1)
        self.assertEqual(guardado[0]["total"], 2)

    def test_andamento_em_json_enquanto_roda(self):
        self.semear()
        cookie = self.entrar()
        relatorio_id = self.gerar(cookie)
        self.esperar(cookie, relatorio_id)
        status, cabecalhos, dados = self.pedir("GET", f"/relatorio/{relatorio_id}/andamento.json", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn(b'"estado": "pronto"', dados)

    def test_um_relatorio_por_vez_em_cada_sessao(self):
        cookie = self.entrar()
        sessao = self.site.sessoes.obter(_id_da_sessao(cookie))
        sessao.relatorios["parado"] = relatorios.Relatorio(111222333, 30)  # ainda rodando
        status, _, pagina = self.pedir("POST", "/relatorio/gerar", cookie=cookie, corpo=b"dias=30")
        self.assertEqual(status, 200)
        self.assertIn("Já tem um relatório sendo gerado".encode("utf-8"), pagina)
        status, _, pagina = self.pedir("GET", "/relatorio/parado", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("Gerando seu relatório".encode("utf-8"), pagina)
        status, _, dados = self.pedir("GET", "/relatorio/parado/andamento.json", cookie=cookie)
        self.assertIn(b'"estado": "gerando"', dados)

    def test_pedido_de_outro_site_e_recusado(self):
        cookie = self.entrar()
        status, _, _ = self.pedir("POST", "/relatorio/gerar", cookie=cookie, corpo=b"dias=30",
                                  origem="https://site-estranho.example")
        self.assertEqual(status, 403)
        self.assertEqual(self.site.sessoes.obter(_id_da_sessao(cookie)).relatorios, {})

    def test_outra_sessao_nao_ve_o_relatorio_de_quem_gerou(self):
        self.semear()
        cookie = self.entrar()
        relatorio_id = self.gerar(cookie)
        self.esperar(cookie, relatorio_id)
        outra = self.site.sessoes.criar()
        outra.cliente, outra.usuario = object(), {"id": 999, "apelido": "OUTRA"}
        status, _, _ = self.pedir("GET", f"/relatorio/{relatorio_id}", cookie=f"orzy_sessao={outra.id}")
        self.assertEqual(status, 404)

    def test_token_vencido_pede_novo_login_sem_renovar_sozinho(self):
        self.semear()
        cookie = self.entrar()
        self.ml.revogar_access_tokens()
        antes = len(self.chamadas_de_token())
        relatorio_id = self.gerar(cookie)
        relatorio = self.esperar(cookie, relatorio_id)
        self.assertEqual(relatorio.estado, relatorios.ERRO)
        self.assertIn("venceu", relatorio.mensagem)
        self.assertEqual(len(self.chamadas_de_token()), antes, "o site não pode renovar com refresh token")
        status, _, pagina = self.pedir("GET", f"/relatorio/{relatorio_id}", cookie=cookie)
        self.assertIn("Tentar de novo".encode("utf-8"), pagina)

    def test_conta_sem_anuncios_avisa_sem_erro(self):
        cookie = self.entrar()
        relatorio_id = self.gerar(cookie)
        relatorio = self.esperar(cookie, relatorio_id)
        self.assertEqual(relatorio.estado, relatorios.PRONTO)
        self.assertEqual(relatorio.mensagem, "Nenhum anúncio ativo nessa conta.")
        status, _, pagina = self.pedir("GET", f"/relatorio/{relatorio_id}", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("Nenhum anúncio ativo nessa conta.".encode("utf-8"), pagina)


class HistoricoSiteTests(SiteBase):
    def test_historico_vazio(self):
        cookie = self.entrar()
        status, _, pagina = self.pedir("GET", "/historico", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("Você ainda não tem relatórios guardados".encode("utf-8"), pagina)

    def test_ver_apagar_com_confirmacao(self):
        self.semear()
        cookie = self.entrar()
        relatorio_id = self.gerar(cookie)
        self.esperar(cookie, relatorio_id)

        status, _, pagina = self.pedir("GET", "/historico", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn(f"/historico/{self.site.historico.listar(111222333)[0]['id']}".encode("utf-8"), pagina)

        status, _, pagina = self.pedir("GET", f"/historico/{self.site.historico.listar(111222333)[0]['id']}",
                                       cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("não é atualizado depois".encode("utf-8"), pagina)

        status, _, _ = self.pedir("POST", "/historico/apagar", cookie=cookie, corpo=b"")
        self.assertEqual(status, 400, "apagar sem confirmar não pode")
        self.assertEqual(len(self.site.historico.listar(111222333)), 1)

        status, cabecalhos, _ = self.pedir("POST", "/historico/apagar", cookie=cookie, corpo=b"confirmo=on")
        self.assertEqual(status, 303)
        self.assertEqual(self.site.historico.listar(111222333), [])

    def test_compara_com_o_relatorio_anterior_do_mesmo_periodo(self):
        self.semear()
        self.ml.adicionar_item("MLB1000000003", "Capa <b>antiga</b> para celular", visitas=50)
        cookie = self.entrar()
        primeiro = self.gerar(cookie)
        self.esperar(cookie, primeiro)
        self.assertNotIn(b"#mudancas", self.pedir("GET", f"/relatorio/{primeiro}", cookie=cookie)[2],
                         "sem relatório anterior, não há o que comparar")
        guardado_1 = self.site.historico.listar(111222333)[0]["id"]
        texto = self.pedir("GET", f"/historico/{guardado_1}", cookie=cookie)[2].decode("utf-8")
        self.assertIn("Ainda não há um relatório anterior de 30 dias para comparar", texto)

        # Entre um relatório e outro, o vendedor mudou o título do fone, que passou a ter visitas e vendas;
        # a capa saiu dos anúncios ativos e entrou um suporte.
        self.ml.itens["MLB1000000001"]["title"] = "Fone Bluetooth <script>x</script> Novo"
        self.ml.visitas["MLB1000000001"] = 200
        self.ml.adicionar_pedido("MLB1000000001", quantidade=5, dias_atras=1)
        self.ml.itens["MLB1000000003"]["status"] = "paused"
        self.ml.adicionar_item("MLB1000000004", "Suporte de mesa", visitas=10)
        self.esperar(cookie, self.gerar(cookie, dias=60))  # outro período: fica fora da comparação
        segundo = self.gerar(cookie)
        self.esperar(cookie, segundo)
        guardado_2 = self.site.historico.listar(111222333)[0]["id"]

        pagina = self.pedir("GET", f"/relatorio/{segundo}", cookie=cookie)[2].decode("utf-8")
        self.assertIn(f'<a href="/historico/{guardado_2}#mudancas">Ver o que mudou', pagina)

        texto = self.pedir("GET", f"/historico/{guardado_2}", cookie=cookie)[2].decode("utf-8")
        self.assertIn('<h2 id="mudancas">', texto)
        self.assertIn(f'<a href="/historico/{guardado_1}">', texto, "compara com o de 30 dias, não com o de 60")
        self.assertIn("Mostra o que\nmudou, não o porquê", texto)
        self.assertIn("Mudaram de situação: 1", texto)
        self.assertIn("Novos neste relatório: 1", texto)
        self.assertIn("Não estão mais no relatório: 1", texto)
        self.assertIn("Títulos que mudaram: 1", texto)
        self.assertIn("<td class=n>0 → 200 (+200)</td><td class=n>0 → 5 (+5)</td>", texto)
        self.assertIn("POUCA VISITA → VENDENDO BEM", texto)
        self.assertIn(f"Título antes: {TITULO_BOM}", texto)
        self.assertIn("Fone Bluetooth &lt;script&gt;x&lt;/script&gt; Novo", texto)
        self.assertNotIn("<script>x", texto)
        self.assertIn("<li>Capa &lt;b&gt;antiga&lt;/b&gt; para celular</li>", texto)
        self.assertIn('Suporte de mesa<br><span class="ajuda">Novo neste relatório</span>', texto)


class PaginasSimplesTests(SiteBase):
    def test_privacidade_e_cabecalhos_de_seguranca(self):
        status, cabecalhos, pagina = self.pedir("GET", "/privacidade", origem=None)
        self.assertEqual(status, 200)
        self.assertIn("Política de Privacidade".encode("utf-8"), pagina)
        self.assertIn("ainda está sendo preparado".encode("utf-8"), pagina, "sem o arquivo, a página avisa")
        self.assertEqual(_cab(cabecalhos, "Referrer-Policy"), "no-referrer")
        self.assertEqual(_cab(cabecalhos, "X-Frame-Options"), "DENY")
        self.assertIn("default-src 'self'", _cab(cabecalhos, "Content-Security-Policy"))

    def test_arquivos_estaticos_so_os_da_lista(self):
        self.assertEqual(self.pedir("GET", "/static/app.py", origem=None)[0], 404)
        status, cabecalhos, _ = self.pedir("GET", "/static/estilo.css", origem=None)
        self.assertEqual(status, 200)
        self.assertEqual(_cab(cabecalhos, "Content-Type"), "text/css; charset=utf-8")

    def test_robots_e_descricao_para_buscadores(self):
        status, cabecalhos, corpo = self.pedir("GET", "/robots.txt", origem=None)
        self.assertEqual(status, 200)
        self.assertEqual(_cab(cabecalhos, "Content-Type"), "text/plain; charset=utf-8")
        for caminho in ("/entrar", "/retorno", "/relatorio", "/historico"):
            self.assertIn(f"Disallow: {caminho}\n".encode(), corpo)
        self.assertNotIn(b"Disallow: /\n", corpo, "a página inicial e os textos legais continuam abertos")
        inicio = self.pedir("GET", "/", origem=None)[2].decode("utf-8")
        self.assertIn('<meta name="description" content="Conecte sua conta do Mercado Livre', inicio)

    def test_palavra_sem_espaco_quebra_no_celular(self):
        # Apelidos como LOJA_DO_JOAO_OFICIAL, no título, empurravam a página para o lado num celular de 360 px.
        status, _, css = self.pedir("GET", "/static/estilo.css", origem=None)
        self.assertEqual(status, 200)
        corpo = css.decode("utf-8")
        regra = corpo[corpo.index("\nbody {"):]
        self.assertIn("overflow-wrap: break-word", regra[:regra.index("}")])

    def test_pagina_que_nao_existe(self):
        self.assertEqual(self.pedir("GET", "/nao-existe", origem=None)[0], 404)

    def test_textos_legais_vem_de_docs_legal_com_escape(self):
        self.pasta_legal.mkdir()
        (self.pasta_legal / "termos-de-uso.md").write_text(
            "# Termos de Uso do Orzy\n\n"
            "> **Rascunho.** O que falta está no [LEIA-ME](LEIA-ME.md).\n\n"
            "Texto com <script>alert(1)</script> e o cookie `orzy_sessao`,\n"
            "que continua na linha de baixo.\n\n"
            "- um item que segue\n  na linha seguinte;\n- leia a [Política](politica-de-privacidade.md).\n\n"
            "| Dado | Prazo |\n|---|---|\n| Código de renovação | Não é guardado |\n\n"
            "[clique](javascript:alert(1)) ou veja a [ANPD](https://www.gov.br/anpd).\n\n"
            "Escreva para [o Orzy](mailto:orzy.suporte@gmail.com).\n",
            encoding="utf-8")
        status, _, pagina = self.pedir("GET", "/termos", origem=None)
        texto = pagina.decode("utf-8")
        self.assertEqual(status, 200)
        self.assertIn("<title>Termos de Uso · Orzy</title>", texto)
        self.assertIn("<h1>Termos de Uso do Orzy</h1>", texto)
        self.assertIn("<blockquote><p><strong>Rascunho.</strong> O que falta está no LEIA-ME.</p></blockquote>", texto)
        self.assertNotIn("<script>alert", texto)
        self.assertIn("&lt;script&gt;", texto)
        self.assertIn("<code>orzy_sessao</code>, que continua na linha de baixo.", texto)
        self.assertIn("<li>um item que segue na linha seguinte;</li>", texto)
        self.assertIn('<a href="/privacidade">Política</a>', texto, "um texto aponta para a rota do outro")
        self.assertIn("<td>Código de renovação</td><td>Não é guardado</td>", texto)
        self.assertNotIn("javascript:", texto)
        self.assertIn('<a href="https://www.gov.br/anpd"', texto)
        self.assertIn('<a href="mailto:orzy.suporte@gmail.com">o Orzy</a>', texto, "e-mail sem abrir aba vazia")

    def test_rodape_tem_os_dois_textos_em_todas_as_paginas(self):
        cookie = self.entrar()
        for caminho, com_cookie in (("/", None), ("/nao-existe", None), ("/relatorio", cookie),
                                    ("/historico", cookie)):
            texto = self.pedir("GET", caminho, cookie=com_cookie, origem=None)[2].decode("utf-8")
            rodape = texto[texto.index('<footer class="rodape">'):]
            self.assertIn('href="/privacidade"', rodape, caminho)
            self.assertIn('href="/termos"', rodape, caminho)
            self.assertIn('href="mailto:orzy.suporte@gmail.com"', rodape, caminho)

    def test_inicio_sem_login_leva_ao_mercado_livre(self):
        status, _, pagina = self.pedir("GET", "/", origem=None)
        self.assertEqual(status, 200)
        texto = pagina.decode("utf-8")
        self.assertIn('href="/entrar"', texto)
        self.assertNotIn('href="/relatorio"', texto)
        self.assertIn('href="/privacidade"', texto)
        # Junto de cada botão Conectar, o aviso dos Termos de Uso e da Política de Privacidade.
        self.assertEqual(texto.count('href="/entrar"'), texto.count("Ao conectar, você aceita os"))
        self.assertIn('<a href="/termos">Termos de Uso</a>', texto)
        # A política de segurança do site (CSP) bloqueia estilo e script escritos dentro da página.
        self.assertNotIn("style=", texto)
        self.assertNotIn("<style", texto)
        self.assertNotIn("<script", texto)

    def test_inicio_com_login_leva_ao_relatorio(self):
        cookie = self.entrar()
        status, _, pagina = self.pedir("GET", "/", cookie=cookie, origem=None)
        self.assertEqual(status, 200)
        texto = pagina.decode("utf-8")
        self.assertIn('class="botao botao-grande" href="/relatorio"', texto)
        self.assertNotIn('href="/entrar"', texto)
        self.assertNotIn("Ao conectar", texto)

    def test_inicio_acompanha_os_limites_do_analise(self):
        with mock.patch.object(analise, "POUCAS_VISITAS", 50), mock.patch.object(analise, "CONVERSAO_BAIXA", 0.02):
            texto = self.pedir("GET", "/", origem=None)[2].decode("utf-8")
        self.assertIn("Menos de 50 visitas e nenhuma venda", texto)
        self.assertIn("menos de 1 venda a cada 50 visitas", texto)


class ServidorTests(SiteBase):
    def test_responde_por_http_de_verdade(self):
        manipulador = type("ManipuladorTeste", (servidor.Manipulador,), {"site": self.site})
        http_server = ThreadingHTTPServer(("127.0.0.1", 0), manipulador)
        threading.Thread(target=http_server.serve_forever, daemon=True).start()
        self.addCleanup(http_server.server_close)
        self.addCleanup(http_server.shutdown)
        porta = http_server.server_address[1]

        conexao = http.client.HTTPConnection("127.0.0.1", porta, timeout=10)
        conexao.request("GET", "/saude")
        resposta = conexao.getresponse()
        self.assertEqual((resposta.status, resposta.read()), (200, b"ok"))

        # HEAD (verificadores de link): os cabeçalhos do GET, sem o corpo.
        with socket.create_connection(("127.0.0.1", porta), timeout=10) as s:
            s.sendall(b"HEAD /termos HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n")
            bruto = b""
            while pedaco := s.recv(65536):
                bruto += pedaco
        cabecalho, _, corpo = bruto.partition(b"\r\n\r\n")
        self.assertTrue(cabecalho.startswith(b"HTTP/1.0 200"), cabecalho[:40])
        self.assertIn(b"Content-Type: text/html; charset=utf-8", cabecalho)
        self.assertEqual(corpo, b"", "HEAD não manda o corpo")

        conexao.request("POST", "/sair", body=b"", headers={"Origin": "https://site-estranho.example",
                                                            "Content-Length": "0"})
        resposta = conexao.getresponse()
        self.assertEqual(resposta.status, 403)
        resposta.read()
        conexao.close()


class ConexaoParadaTests(SiteBase):
    def test_conexao_parada_e_fechada_sem_erro(self):
        self.assertTrue(0 < servidor.Manipulador.timeout <= 120, "o servidor de verdade tem tempo máximo por conexão")
        manipulador = type("ManipuladorTeste", (servidor.Manipulador,), {"site": self.site, "timeout": 0.3})
        http_server = ThreadingHTTPServer(("127.0.0.1", 0), manipulador)
        erros = []
        http_server.handle_error = lambda pedido, endereco: erros.append(sys.exc_info()[1])
        threading.Thread(target=http_server.serve_forever, daemon=True).start()
        self.addCleanup(http_server.server_close)
        self.addCleanup(http_server.shutdown)
        porta = http_server.server_address[1]

        with socket.create_connection(("127.0.0.1", porta), timeout=10) as s:
            self.assertEqual(s.recv(1), b"", "o servidor fecha a conexão que não manda nada")
        conexao = http.client.HTTPConnection("127.0.0.1", porta, timeout=10)
        conexao.request("GET", "/saude")
        self.assertEqual(conexao.getresponse().status, 200, "e continua atendendo")
        conexao.close()
        self.assertEqual(erros, [])


class LimpezaDoHistoricoTests(unittest.TestCase):
    def test_apaga_o_historico_antigo_todo_dia_e_segue_depois_de_um_erro(self):
        parar = threading.Event()
        chamadas = []

        class HistoricoFalso:
            def apagar_antigos(self, dias):
                chamadas.append(dias)
                if len(chamadas) == 1:
                    raise sqlite3.OperationalError("database is locked")
                if len(chamadas) == 3:
                    parar.set()
                return 0

        with self.assertLogs(level="ERROR"):
            servidor.apagar_antigos_todo_dia(HistoricoFalso(), parar, intervalo=0.01)
        self.assertEqual(chamadas, [365, 365, 365], "um erro não pode parar a limpeza dos dias seguintes")


if __name__ == "__main__":
    unittest.main()
