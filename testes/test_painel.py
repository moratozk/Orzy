"""
Testes do painel contra o Mercado Livre simulado (ml_simulado.py).

Rodar, na pasta principal do Orzy:
    python -m unittest discover -s testes -v

Nada aqui fala com o Mercado Livre de verdade, e a sua pasta painel-ml não é tocada:
login e relatórios dos testes ficam numa pasta temporária.
"""

import contextlib
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path
from unittest import mock

PASTA_TESTES = Path(__file__).resolve().parent
PASTA_PAINEL = PASTA_TESTES.parent / "painel-ml"
sys.path.insert(0, str(PASTA_PAINEL))
sys.path.insert(0, str(PASTA_TESTES))

import analise  # noqa: E402
import conectar  # noqa: E402
import meus_anuncios  # noqa: E402
import ml_api  # noqa: E402
from ml_simulado import ATRIBUTOS_PADRAO, MLSimulado, performance  # noqa: E402

CLIENT_ID = "1234567890"
SECRET = "segredo-de-teste"

TITULO_BOM = "Fone de Ouvido Bluetooth Sem Fio Marca Teste Modelo X1 Preto"  # 60 caracteres


class Base(unittest.TestCase):
    exigir_pkce = False

    def setUp(self):
        self.ml = MLSimulado(client_id=CLIENT_ID, client_secret=SECRET, exigir_pkce=self.exigir_pkce)
        base = self.ml.iniciar()
        self.addCleanup(self.ml.parar)

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.pasta = Path(temp.name)

        # Aponta o painel para o simulado e para a pasta temporária.
        for trocar in [
            mock.patch.object(ml_api, "API_BASE", base),
            mock.patch.object(ml_api, "AUTH_URL", base + "/authorization"),
            mock.patch.object(ml_api, "ARQ_CONFIG", self.pasta / "config.json"),
            mock.patch.object(ml_api, "ARQ_TOKENS", self.pasta / "tokens.json"),
            mock.patch.object(meus_anuncios, "ARQ_RELATORIO", self.pasta / "relatorio_anuncios.csv"),
        ]:
            trocar.start()
            self.addCleanup(trocar.stop)
        dormir = mock.patch("time.sleep")  # as esperas entre tentativas não precisam passar de verdade
        self.sleep = dormir.start()
        self.addCleanup(dormir.stop)

    # ------------------------------------------------------------ ajudantes

    def rodar_conectar(self, respostas, argv=("conectar.py",)):
        """Roda o conectar.py respondendo às perguntas na ordem.

        Uma resposta pode ser uma função: ela recebe o link de login que o programa
        abriu no navegador e devolve o que a pessoa colaria.
        """
        links = []
        fila = list(respostas)

        def falso_input(prompt=""):
            resposta = fila.pop(0)
            return resposta(links[-1]) if callable(resposta) else resposta

        saida = io.StringIO()
        with mock.patch("builtins.input", falso_input), \
                mock.patch("getpass.getpass", falso_input), \
                mock.patch("webbrowser.open", lambda url: links.append(url) or True), \
                mock.patch.object(sys, "argv", list(argv)), \
                contextlib.redirect_stdout(saida):
            try:
                conectar.main()
                codigo = 0
            except SystemExit as e:
                codigo = e.code
        return codigo, saida.getvalue(), links

    def login(self, pkce=False):
        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "s" if pkce else "n", self.ml.autorizar])
        self.assertEqual(codigo, 0, saida)
        return saida

    def rodar_relatorio(self, *args):
        saida = io.StringIO()
        with mock.patch.object(sys, "argv", ["meus_anuncios.py", *args]), contextlib.redirect_stdout(saida):
            try:
                meus_anuncios.main()
                codigo = 0
            except SystemExit as e:
                codigo = e.code
        return codigo, saida.getvalue()

    def ler_csv(self, caminho=None):
        with open(caminho or self.pasta / "relatorio_anuncios.csv", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f, delimiter=";"))

    def ler_tokens(self):
        return json.loads((self.pasta / "tokens.json").read_text(encoding="utf-8"))


# ================================================================ login

class TestLogin(Base):

    def test_primeiro_login_salva_config_e_tokens(self):
        saida = self.login()
        self.assertIn("Pronto! Conectado como LOJA_TESTE", saida)
        self.assertIn("O login se renova sozinho", saida)
        config = json.loads((self.pasta / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["redirect_uri"], "https://www.google.com")
        self.assertFalse(config["usar_pkce"])
        tokens = self.ler_tokens()
        self.assertTrue(tokens["refresh_token"])
        self.assertEqual(tokens["user_id"], self.ml.usuario["id"])

    def test_link_de_login_tem_o_que_o_mercado_livre_pede(self):
        _, _, links = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", self.ml.autorizar])
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(links[0]).query))
        self.assertEqual(params["response_type"], "code")
        self.assertEqual(params["client_id"], CLIENT_ID)
        self.assertEqual(params["redirect_uri"], "https://www.google.com")
        self.assertTrue(params["state"])
        self.assertNotIn("code_challenge", params)

    def test_aceita_so_o_codigo_colado(self):
        def so_o_codigo(link):
            return urllib.parse.parse_qs(urllib.parse.urlparse(self.ml.autorizar(link)).query)["code"][0]

        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", so_o_codigo])
        self.assertEqual(codigo, 0, saida)

    def test_aceita_endereco_sem_https_e_com_aspas(self):
        def colado_torto(link):
            return '"' + self.ml.autorizar(link).replace("https://", "") + '"  '

        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", colado_torto])
        self.assertEqual(codigo, 0, saida)

    def test_colou_errado_e_pode_colar_de_novo(self):
        # Foi o que aconteceu no primeiro teste de verdade: digitou o exemplo do passo a passo.
        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", "code=TG-...", self.ml.autorizar])
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não achei o código", saida)
        self.assertIn("O login continua esperando", saida)
        self.assertIn("Pronto! Conectado como LOJA_TESTE", saida)

    def test_endereco_de_outra_tentativa_e_recusado(self):
        def outro_state(link):
            return self.ml.autorizar(link).replace("state=", "state=x")

        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", outro_state])
        self.assertEqual(codigo, 1)
        self.assertIn("outra tentativa de login", saida)

    def test_codigo_usado_duas_vezes(self):
        colados = []

        def guardar(link):
            colados.append(self.ml.autorizar(link))
            return colados[-1]

        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", guardar])
        self.assertEqual(codigo, 0, saida)
        # Cola de novo o mesmo código, agora numa nova tentativa de login.
        codigo, saida, _ = self.rodar_conectar([lambda link: _com_state(colados[0], _state(link))])
        self.assertEqual(codigo, 1)
        self.assertIn("O código não foi aceito", saida)

    def test_secret_errado(self):
        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, "secret-errado", "", "n", self.ml.autorizar])
        self.assertEqual(codigo, 1)
        self.assertIn("Client ID ou Client Secret incorretos", saida)

    def test_recusou_no_navegador(self):
        def recusou(link):
            return "https://www.google.com/?error=access_denied&error_description=user+denied&state=" + _state(link)

        codigo, saida, _ = self.rodar_conectar([CLIENT_ID, SECRET, "", "n", recusou])
        self.assertEqual(codigo, 1)
        self.assertIn("recusou a autorização", saida)

    def test_secret_nao_aparece_na_tela(self):
        class Teclado:  # um Prompt de Comando de verdade, e não uma entrada redirecionada
            def isatty(self):
                return True

        escondidos = []

        def falso_getpass(prompt=""):
            escondidos.append(prompt)
            return SECRET

        respostas = iter([CLIENT_ID, "", "n"])
        with mock.patch.object(sys, "stdin", Teclado()), \
                mock.patch("builtins.input", lambda prompt="": next(respostas)), \
                mock.patch("getpass.getpass", falso_getpass), \
                contextlib.redirect_stdout(io.StringIO()) as saida:
            config = conectar.configurar()
        self.assertEqual(config["client_secret"], SECRET)
        self.assertEqual(len(escondidos), 1)
        self.assertIn("Client Secret", escondidos[0])
        self.assertIn("a chave não aparece na tela", saida.getvalue())
        self.assertNotIn(SECRET, saida.getvalue())

    def test_refazer_pergunta_os_dados_de_novo(self):
        self.login()
        self.rodar_conectar(["999", "outro", "", "n", lambda link: "TG-qualquer"], argv=("conectar.py", "--refazer"))
        config = json.loads((self.pasta / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["client_id"], "999")

    def test_segunda_vez_nao_pergunta_os_dados_do_app(self):
        self.login()
        codigo, saida, _ = self.rodar_conectar([self.ml.autorizar])
        self.assertEqual(codigo, 0, saida)
        self.assertNotIn("Client ID", saida)


class TestLoginComPKCE(Base):
    exigir_pkce = True

    def test_login_com_pkce(self):
        _, _, links = self.rodar_conectar([CLIENT_ID, SECRET, "", "s", self.ml.autorizar])
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(links[0]).query))
        self.assertEqual(params["code_challenge_method"], "S256")
        self.assertTrue(json.loads((self.pasta / "config.json").read_text(encoding="utf-8"))["usar_pkce"])
        self.assertTrue(self.ler_tokens()["access_token"])


def _state(link):
    return urllib.parse.parse_qs(urllib.parse.urlparse(link).query)["state"][0]


def _com_state(endereco, state):
    return re.sub(r"state=[^&]*", "state=" + state, endereco)


# ================================================================ cliente da API

class TestCliente(Base):

    def setUp(self):
        super().setUp()
        self.login()

    def test_renova_token_vencido_e_salva_o_novo_na_hora(self):
        tokens = self.ler_tokens()
        antigo = tokens["refresh_token"]
        tokens["expira_em"] = 0
        (self.pasta / "tokens.json").write_text(json.dumps(tokens), encoding="utf-8")

        ml_api.MercadoLivre().obter_usuario()

        novo = self.ler_tokens()
        self.assertNotEqual(novo["refresh_token"], antigo)
        self.assertFalse(self.ml.refresh_ainda_vale(antigo), "o refresh token é de uso único")
        self.assertTrue(self.ml.refresh_ainda_vale(novo["refresh_token"]))

    def test_token_recusado_antes_da_hora_renova_uma_vez(self):
        cliente = ml_api.MercadoLivre()
        self.ml.revogar_access_tokens()
        self.assertEqual(cliente.obter_usuario()["nickname"], "LOJA_TESTE")

    def test_permissao_retirada_pede_login_de_novo(self):
        cliente = ml_api.MercadoLivre()
        self.ml.revogar_tudo()
        with self.assertRaises(ml_api.ErroLogin) as erro:
            cliente.obter_usuario()
        self.assertIn("python conectar.py", str(erro.exception))

    def test_erro_429_espera_e_tenta_de_novo(self):
        cliente = ml_api.MercadoLivre()
        self.sleep.reset_mock()
        self.ml.falhas = [429, 429]
        self.assertEqual(cliente.obter_usuario()["nickname"], "LOJA_TESTE")
        self.assertEqual([c.args[0] for c in self.sleep.call_args_list], [2, 4])

    def test_erro_429_que_nao_passa_vira_mensagem(self):
        cliente = ml_api.MercadoLivre()
        self.ml.falhas = [429] * 4
        with self.assertRaises(ml_api.ErroML) as erro:
            cliente.obter_usuario()
        self.assertEqual(erro.exception.status, 429)

    def test_conexao_que_cai_no_meio_tenta_de_novo(self):
        cliente = ml_api.MercadoLivre()
        self.ml.falhas = ["derrubar"]
        self.assertEqual(cliente.obter_usuario()["nickname"], "LOJA_TESTE")

    def test_conexao_que_cai_sempre_vira_mensagem(self):
        cliente = ml_api.MercadoLivre()
        self.ml.falhas = ["derrubar"] * 4
        with self.assertRaises(ml_api.ErroML) as erro:
            cliente.obter_usuario()
        self.assertIn("Sem conexão", str(erro.exception))

    def test_rede_com_bloqueio_vira_mensagem(self):
        cliente = ml_api.MercadoLivre()
        self.ml.falhas = ["html"]
        with self.assertRaises(ml_api.ErroML) as erro:
            cliente.obter_usuario()
        self.assertIn("respondeu algo inesperado", str(erro.exception))

    def test_sem_internet_vira_mensagem(self):
        cliente = ml_api.MercadoLivre()
        with mock.patch.object(ml_api, "API_BASE", "http://127.0.0.1:9"):
            with self.assertRaises(ml_api.ErroML) as erro:
                cliente.get("/users/me")
        self.assertIn("Sem conexão", str(erro.exception))

    def test_sem_permissao_vira_mensagem(self):
        cliente = ml_api.MercadoLivre()
        self.ml.erros_por_rota["/users/me"] = 403
        with self.assertRaises(ml_api.ErroML) as erro:
            cliente.obter_usuario()
        self.assertIn("Sem permissão", str(erro.exception))


# ================================================================ relatório

class TestRelatorio(Base):

    def setUp(self):
        super().setUp()
        self.login()

    def montar_loja(self):
        ml = self.ml
        ml.adicionar_item("MLB100", "Fone sem fio", preco=1234.56, visitas=500)       # visita sem venda
        ml.adicionar_item("MLB200", "Capa de celular", preco=29.9, visitas=1000)     # converte pouco
        ml.adicionar_item("MLB300", "Cabo USB-C", preco=19.9, visitas=10)            # pouca visita
        ml.adicionar_item("MLB400", "Carregador turbo", preco=79.9, visitas=20)      # vende, mas pouco visto
        ml.adicionar_item("MLB500", "Suporte veicular", preco=49.9, visitas=200)     # vendendo bem
        ml.adicionar_item("MLB600", "Película 3D", preco=9.9, visitas=None)          # erro nas visitas
        ml.adicionar_item("MLB700", "Anúncio pausado", visitas=999, status="paused")

        ml.adicionar_pedido("MLB200", quantidade=3, dias_atras=2)
        ml.adicionar_pedido("MLB200", quantidade=2, dias_atras=10)
        ml.adicionar_pedido("MLB400", quantidade=3, dias_atras=5)
        for dia in range(10):
            ml.adicionar_pedido("MLB500", dias_atras=dia + 1)
        ml.adicionar_pedido("MLB100", dias_atras=45)                     # fora dos 30 dias
        ml.adicionar_pedido("MLB300", dias_atras=3, status="cancelled")  # cancelado não conta
        ml.adicionar_pedido("MLB300", dias_atras=3, status="payment_required")  # não pago não conta

    def test_relatorio_completo(self):
        self.montar_loja()
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)

        linhas = self.ler_csv()
        self.assertEqual(list(linhas[0].keys()), ["id", "titulo", "preco", "estoque", "visitas_30d", "vendas_30d",
                                                  "conversao_%", "situacao", "o_que_olhar", "o_que_mudar",
                                                  "qualidade_ml", "fotos", "ficha_tecnica", "link"])
        por_id = {l["id"]: l for l in linhas}
        self.assertNotIn("MLB700", por_id, "anúncio pausado não entra")
        self.assertEqual([l["id"] for l in linhas], ["MLB100", "MLB200", "MLB300", "MLB400", "MLB500", "MLB600"])
        self.assertEqual({i: l["situacao"] for i, l in por_id.items()}, {
            "MLB100": "VISITA SEM VENDA",
            "MLB200": "CONVERTE POUCO",
            "MLB300": "POUCA VISITA",
            "MLB400": "VENDE, MAS POUCO VISTO",
            "MLB500": "VENDENDO BEM",
            "MLB600": "SEM DADOS",
        })
        self.assertEqual(por_id["MLB100"]["preco"], "1.234,56")
        self.assertEqual(por_id["MLB100"]["vendas_30d"], "0")
        self.assertEqual(por_id["MLB200"]["vendas_30d"], "5")
        self.assertEqual(por_id["MLB200"]["conversao_%"], "0,5")
        self.assertEqual(por_id["MLB500"]["conversao_%"], "5,0")
        self.assertEqual(por_id["MLB600"]["visitas_30d"], "?")
        self.assertTrue(por_id["MLB100"]["link"].startswith("https://"))
        self.assertTrue(por_id["MLB100"]["o_que_mudar"].startswith("1) Título curto (12 de 60 caracteres)"))
        self.assertEqual(por_id["MLB100"]["qualidade_ml"], "ainda sem nota")
        self.assertIn("O Mercado Livre ainda não tem nota para nenhum dos anúncios (resposta: Not found item "
                      "performance)", saida)

        self.assertIn("Comece por estes", saida)
        self.assertIn("Os que mais vendem", saida)
        self.assertIn("Relatório completo salvo em", saida)

    def test_periodo_maior_conta_vendas_mais_antigas(self):
        self.montar_loja()
        codigo, saida = self.rodar_relatorio("--dias", "60")
        self.assertEqual(codigo, 0, saida)
        por_id = {l["id"]: l for l in self.ler_csv()}
        self.assertEqual(por_id["MLB100"]["vendas_60d"], "1")
        visitas = [c[2] for c in self.ml.chamadas if c[1].endswith("/visits/time_window")]
        self.assertTrue(all(p["last"] == "60" for p in visitas))

    def test_periodo_fora_do_limite_fica_em_150_dias(self):
        self.montar_loja()
        codigo, saida = self.rodar_relatorio("--dias", "999")
        self.assertEqual(codigo, 0, saida)
        self.assertIn("últimos 150 dias", saida)

    def test_muitos_pedidos_paginados(self):
        self.ml.adicionar_item("MLB100", "Produto campeão", visitas=5000)
        for _ in range(130):
            self.ml.adicionar_pedido("MLB100", dias_atras=1)
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(self.ler_csv()[0]["vendas_30d"], "130")

    def test_mais_de_1000_anuncios_usa_scan_e_multiget_de_20(self):
        for n in range(1205):
            self.ml.adicionar_item(f"MLB{900000 + n}", f"Produto {n}", visitas=n % 50)
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        linhas = self.ler_csv()
        self.assertEqual(len(linhas), 1205)
        self.assertEqual(len({l["id"] for l in linhas}), 1205)
        self.assertTrue(all(l["titulo"] for l in linhas), "todo anúncio precisa vir com os detalhes")
        buscas = [c[2] for c in self.ml.chamadas if c[1].endswith("/items/search")]
        self.assertTrue(any(p.get("search_type") == "scan" for p in buscas))
        multigets = [c[2] for c in self.ml.chamadas if c[1] == "/items"]
        self.assertTrue(all(len(p["ids"].split(",")) <= 20 for p in multigets))

    def test_ate_1000_anuncios_usa_paginas_normais(self):
        for n in range(1000):
            self.ml.adicionar_item(f"MLB{900000 + n}", f"Produto {n}", visitas=1)
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertEqual(len(self.ler_csv()), 1000)

    def test_sem_permissao_para_vendas_mostra_interrogacao(self):
        self.montar_loja()
        self.ml.erros_por_rota["/orders/search"] = 403
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não consegui ler as vendas", saida)
        linhas = self.ler_csv()
        self.assertTrue(all(l["vendas_30d"] == "?" and l["situacao"] == "SEM DADOS" for l in linhas))

    def test_sem_permissao_para_visitas_avisa_o_motivo(self):
        self.montar_loja()
        self.ml.erros_por_rota["/items/"] = 403
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não consegui ler as visitas de 6 anúncio(s)", saida)
        self.assertIn("Sem permissão", saida)
        self.assertTrue(all(l["situacao"] == "SEM DADOS" for l in self.ler_csv()))

    def test_csv_aberto_no_excel_salva_com_outro_nome(self):
        self.montar_loja()
        abrir = open
        tentativas = []

        def falso_open(caminho, *args, **kwargs):
            tentativas.append(Path(caminho))
            if len(tentativas) == 1:
                raise PermissionError("o arquivo está aberto no Excel")
            return abrir(caminho, *args, **kwargs)

        with mock.patch.object(meus_anuncios, "open", falso_open, create=True):
            codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertRegex(tentativas[1].name, r"^relatorio_anuncios_\d{8}_\d{6}\.csv$")
        self.assertEqual(len(self.ler_csv(tentativas[1])), 6)

    def test_conta_sem_anuncios(self):
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Nenhum anúncio ativo", saida)
        self.assertFalse((self.pasta / "relatorio_anuncios.csv").exists())

    def test_login_vencido_durante_o_relatorio(self):
        self.montar_loja()
        self.ml.revogar_tudo()
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 1)
        self.assertIn("python conectar.py", saida)


    def test_sugestoes_e_nota_do_ml_no_relatorio(self):
        ml = self.ml
        ml.adicionar_item("MLB100", "Fone Bluetooth", visitas=500, fotos=1, frete_gratis=False,
                          ficha={"BRAND": "Genérica", "LINE": None, "WITH_BLUETOOTH": "Sim"},
                          qualidade=performance("MLB100", 40, "Bad", "Básica", [
                              ("FREE_SHIPPING", "HAS_FREE_SHIPPING",
                               "Ofereça frete grátis para que seu anúncio seja mais competitivo")]))
        ml.adicionar_item("MLB200", TITULO_BOM, visitas=10,
                          qualidade=performance("MLB200", 95, "Good", "Profissional"))
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)

        por_id = {l["id"]: l for l in self.ler_csv()}
        mudar = por_id["MLB100"]["o_que_mudar"]
        self.assertIn("Coloque pelo menos 3 fotos", mudar)
        self.assertIn("(tem 1)", mudar)
        self.assertIn("Faltam: Modelo (obrigatório)", mudar)
        self.assertIn("(3 de 4 campos preenchidos)", mudar)
        self.assertIn("Título curto (14 de 60 caracteres)", mudar)
        self.assertIn("Ofereça frete grátis para que seu anúncio seja mais competitivo (pedido do ML).", mudar)
        self.assertNotIn("se a margem permitir", mudar, "o pedido do ML substitui a regra igual do Orzy")
        self.assertIn("Teste o Premium", mudar)
        self.assertEqual(por_id["MLB100"]["qualidade_ml"], "Básica (40/100)")
        self.assertEqual(por_id["MLB100"]["fotos"], "1")
        self.assertEqual(por_id["MLB100"]["ficha_tecnica"], "3 de 4 campos")
        self.assertEqual(por_id["MLB200"]["ficha_tecnica"], "4 de 4 campos")
        self.assertEqual(por_id["MLB200"]["o_que_mudar"], "Nenhuma mudança sugerida")
        self.assertEqual(por_id["MLB200"]["qualidade_ml"], "Profissional (95/100)")

        self.assertIn("Comece por estes (o que mudar em cada um):", saida)
        self.assertIn("Nota do ML: Básica (40/100)  |  Fotos: 1  |  Ficha técnica: 3 de 4 campos", saida)
        self.assertIn("      - Coloque pelo menos 3 fotos", saida)
        self.assertIn("(mais 2 no CSV)", saida)
        self.assertIn("      - Quase ninguém encontra", saida, "sem sugestão, mostra o que olhar na situação")

        campos = [c[2]["attributes"].split(",") for c in self.ml.chamadas if c[1] == "/items"][0]
        for campo in ("title", "pictures", "attributes", "shipping", "listing_type_id", "category_id", "tags"):
            self.assertIn(campo, campos)

    def test_quem_tem_mais_para_mudar_vem_antes_na_mesma_situacao(self):
        self.ml.adicionar_item("MLB300", TITULO_BOM, visitas=20)                       # nada a mudar
        self.ml.adicionar_item("MLB400", "Fone", visitas=5, fotos=1, ficha={})          # muito a mudar
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        linhas = self.ler_csv()
        self.assertEqual([l["situacao"] for l in linhas], ["POUCA VISITA", "POUCA VISITA"])
        self.assertEqual([l["id"] for l in linhas], ["MLB400", "MLB300"])

    def test_ficha_tecnica_lida_uma_vez_por_categoria(self):
        for n in range(3):
            self.ml.adicionar_item(f"MLB10{n}", TITULO_BOM, visitas=50)
        self.ml.adicionar_item("MLB200", TITULO_BOM, visitas=50, categoria="MLB2000")
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        caminhos = [c[1] for c in self.ml.chamadas]
        for categoria in ("MLB1000", "MLB2000"):
            self.assertEqual(caminhos.count(f"/categories/{categoria}"), 1)
            self.assertEqual(caminhos.count(f"/categories/{categoria}/attributes"), 1)

    def test_titulo_curto_usa_o_limite_da_categoria(self):
        self.ml.adicionar_categoria("MLB3000", max_titulo=120)
        self.ml.adicionar_item("MLB100", TITULO_BOM, visitas=50, categoria="MLB3000")
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Título curto (60 de 120 caracteres)", self.ler_csv()[0]["o_que_mudar"])

    def test_sem_permissao_para_a_nota_de_qualidade(self):
        self.montar_loja()
        self.ml.erros_por_rota["/item/"] = 403
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não consegui ler a nota de qualidade de 6 anúncio(s)", saida)
        self.assertIn("Sem permissão", saida)
        linhas = self.ler_csv()
        self.assertEqual(len(linhas), 6)
        self.assertTrue(all(l["qualidade_ml"] == "?" for l in linhas))
        self.assertEqual(sum(1 for c in self.ml.chamadas if c[1].startswith("/item/")), 1,
                         "sem permissão vale para todos: para de perguntar no primeiro")

    def test_login_recusado_na_nota_de_qualidade_nao_perde_o_relatorio(self):
        # A documentação diz que a nota devolve 401 quando quem pergunta não é o dono do anúncio.
        self.montar_loja()
        antigo = self.ler_tokens()["refresh_token"]
        self.ml.erros_por_rota["/item/"] = 401
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não consegui ler a nota de qualidade de 6 anúncio(s)", saida)
        self.assertEqual(len(self.ler_csv()), 6)
        novo = self.ler_tokens()["refresh_token"]
        self.assertNotEqual(novo, antigo)
        self.assertTrue(self.ml.refresh_ainda_vale(novo), "o refresh token novo foi salvo")

    def test_nota_que_falha_nos_3_primeiros_para_de_perguntar(self):
        self.montar_loja()
        self.ml.erros_por_rota["/item/"] = 500
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não consegui ler a nota de qualidade de 6 anúncio(s)", saida)
        self.assertEqual(len(self.ler_csv()), 6)
        tentativas = sum(1 for c in self.ml.chamadas if c[1].startswith("/item/"))
        self.assertEqual(tentativas, 3 * 4, "3 anúncios, 4 tentativas cada")

    def test_erro_na_ficha_tecnica_nao_para_o_relatorio(self):
        self.ml.adicionar_item("MLB100", "Fone sem fio", visitas=50, fotos=1, ficha={})
        self.ml.erros_por_rota["/categories/"] = 500
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 0, saida)
        self.assertIn("Não consegui ler a ficha técnica de 1 categoria(s)", saida)
        mudar = self.ler_csv()[0]["o_que_mudar"]
        self.assertIn("Coloque pelo menos 3 fotos", mudar)
        self.assertNotIn("ficha técnica", mudar)


class TestAnalise(unittest.TestCase):
    """As regras do analise.py, sem Mercado Livre nenhum: só os dados do anúncio."""

    def temas(self, sugestoes):
        return [s["tema"] for s in sugestoes]

    def test_titulo_bom_nao_tem_sugestao(self):
        self.assertEqual(analise.analisar_titulo({"title": TITULO_BOM}), [])

    def test_titulo_curto(self):
        sugestoes = analise.analisar_titulo({"title": "Fone sem fio"})
        self.assertEqual(self.temas(sugestoes), ["titulo_tamanho"])
        self.assertIn("12 de 60 caracteres", sugestoes[0]["texto"])
        self.assertEqual(analise.analisar_titulo({"title": "Fone de Ouvido Bluetooth Sem Fio Marca Teste"}), [],
                         "44 caracteres já usam bem o limite de 60")

    def test_palavras_que_o_ml_pede_para_tirar_do_titulo(self):
        sugestoes = analise.analisar_titulo({"title": "Fone Bluetooth PROMOCAO Frete Gratis 50% OFF Lacrado X1"})
        self.assertEqual(self.temas(sugestoes), ["titulo_palavras"])
        texto = sugestoes[0]["texto"]
        for palavra in ("frete grátis", "promoção", "lacrado", "% OFF"):
            self.assertIn(palavra, texto)

    def test_estoque_no_titulo_pode_moderar(self):
        sugestoes = analise.analisar_titulo({"title": "Fone de Ouvido Bluetooth Sem Fio Pronta Entrega"})
        self.assertEqual(sugestoes[0]["tema"], "titulo_estoque")
        self.assertEqual(sugestoes[0]["peso"], analise.ALTA)
        self.assertIn("moderar", sugestoes[0]["texto"])

    def test_titulo_sem_falso_alarme(self):
        for titulo in ("Termômetro Digital -50°C a 300°C Cozinha + Sonda (Preto) 1/2",
                       "Camiseta 100% Algodão USB-C Descontinuado Ofertante 2x Kit"):
            self.assertEqual(analise.analisar_titulo({"title": titulo}), [], titulo)

    def test_simbolos_e_emojis_no_titulo(self):
        sugestoes = analise.analisar_titulo({"title": "Fone de Ouvido Bluetooth!!! Sem Fio ★ Top *Original*"})
        self.assertEqual(self.temas(sugestoes), ["titulo_simbolos"])
        self.assertIn("(! ★ *)", sugestoes[0]["texto"])

    def test_poucas_fotos(self):
        sugestoes = analise.analisar_fotos({"pictures": [{"max_size": "1200x1200"}]})
        self.assertEqual(self.temas(sugestoes), ["fotos_quantidade"])
        self.assertEqual(sugestoes[0]["peso"], analise.ALTA)
        self.assertIn("pelo menos 3 fotos", sugestoes[0]["texto"])
        self.assertIn("(tem 1)", sugestoes[0]["texto"])

    def test_fotos_pequenas_ficam_sem_zoom(self):
        tres = [{"max_size": "500x500"}, {"max_size": "1200x900"}, {"max_size": "800x800"}]
        sugestoes = analise.analisar_fotos({"pictures": tres})
        self.assertEqual(self.temas(sugestoes), ["fotos_tamanho"])
        self.assertIn("2 de 3 fotos têm até 800 px de largura e ficam sem zoom", sugestoes[0]["texto"])
        duas = analise.analisar_fotos({"pictures": [{"max_size": "640x480"}] * 2})
        self.assertIn("As 2 fotos têm até 800 px", duas[-1]["texto"])
        uma = analise.analisar_fotos({"pictures": [{"max_size": "640x480"}]})
        self.assertIn("A foto tem até 800 px de largura e fica sem zoom", uma[-1]["texto"])
        self.assertEqual(analise.analisar_fotos({"pictures": [{"max_size": "1200x1200"}] * 3}), [])
        self.assertEqual(analise.analisar_fotos({"pictures": [{"id": "1"}] * 3}), [], "sem tamanho, não julga")
        self.assertEqual(analise.analisar_fotos({}), [], "sem o campo de fotos, não julga")

    def ficha(self, **valores):
        return [{"id": campo, "value_id": "-1" if valor is None else "1", "value_name": valor}
                for campo, valor in valores.items()]

    def test_ficha_tecnica_sem_campo_obrigatorio(self):
        item = {"attributes": self.ficha(BRAND="Genérica", LINE=None)}  # LINE marcada como "não se aplica"
        sugestoes = analise.analisar_ficha(item, ATRIBUTOS_PADRAO)
        self.assertEqual(len(sugestoes), 1)
        self.assertEqual(sugestoes[0]["peso"], analise.ALTA)
        self.assertIn("(2 de 4 campos preenchidos)", sugestoes[0]["texto"])
        self.assertIn("Faltam: Modelo (obrigatório), Com Bluetooth.", sugestoes[0]["texto"])

    def test_ficha_tecnica_pouco_preenchida(self):
        campos = [{"id": "BRAND", "name": "Marca", "tags": {"required": True}}] + [
            {"id": f"C{n}", "name": f"Campo {n}", "tags": {}} for n in range(1, 8)]
        pouco = analise.analisar_ficha({"attributes": self.ficha(BRAND="X")}, campos)
        self.assertEqual(pouco[0]["peso"], analise.MEDIA)
        self.assertIn("Faltam: Campo 1, Campo 2, Campo 3, Campo 4, Campo 5 e mais 2.", pouco[0]["texto"])
        quase = analise.analisar_ficha({"attributes": self.ficha(BRAND="X", C1="a", C2="b", C3="c", C4="d")}, campos)
        self.assertEqual(quase[0]["peso"], analise.BAIXA)
        completa = self.ficha(BRAND="X", **{f"C{n}": "v" for n in range(1, 8)})
        self.assertEqual(analise.analisar_ficha({"attributes": completa}, campos), [])

    def test_ficha_marcada_incompleta_pelo_ml(self):
        sugestoes = analise.analisar_ficha({"tags": ["incomplete_technical_specs"]}, None)
        self.assertEqual(sugestoes[0]["peso"], analise.ALTA)
        self.assertIn("marcou a ficha técnica", sugestoes[0]["texto"])
        self.assertEqual(analise.analisar_ficha({"tags": []}, None), [], "sem a categoria, não julga")

    def test_frete_gratis_so_quando_o_anuncio_tem_problema(self):
        sem_frete = {"shipping": {"free_shipping": False}}
        for situacao in ("VISITA SEM VENDA", "CONVERTE POUCO", "POUCA VISITA", "VENDE, MAS POUCO VISTO"):
            self.assertEqual(self.temas(analise.analisar_frete(sem_frete, situacao)), ["frete"], situacao)
        for situacao in ("VENDENDO BEM", "SEM DADOS"):
            self.assertEqual(analise.analisar_frete(sem_frete, situacao), [], situacao)
        self.assertEqual(analise.analisar_frete({"shipping": {"free_shipping": True}}, "POUCA VISITA"), [])

    def test_tipo_de_anuncio(self):
        gratis = analise.analisar_tipo({"listing_type_id": "free"}, "POUCA VISITA")
        self.assertEqual(gratis[0]["peso"], analise.ALTA)
        self.assertIn("Grátis para Clássico", gratis[0]["texto"])
        premium = analise.analisar_tipo({"listing_type_id": "gold_special"}, "VISITA SEM VENDA")
        self.assertIn("Teste o Premium", premium[0]["texto"])
        self.assertEqual(analise.analisar_tipo({"listing_type_id": "gold_special"}, "POUCA VISITA"), [])
        self.assertEqual(analise.analisar_tipo({"listing_type_id": "gold_pro"}, "VISITA SEM VENDA"), [])

    def test_nota_de_qualidade_do_ml(self):
        resposta = performance("MLB1", 69, "Average", "Satisfatória", [
            ("PICTURES", "PICTURES_QUANTITY_MIN", "Adicione mais fotos, pelo menos 3."),
            ("SIZE_CHART", "HAS_SIZE_CHART", "Inclua a tabela de medidas", "WARNING")])
        qualidade = analise.ler_qualidade(resposta)
        self.assertEqual(qualidade["nota"], 69)
        self.assertEqual(analise.texto_qualidade(qualidade), "Satisfatória (69/100)")
        textos = [p["texto"] for p in qualidade["pedidos"]]
        self.assertEqual(textos, ["Adicione mais fotos, pelo menos 3 (pedido do ML).",
                                  "Inclua a tabela de medidas (pedido do ML)."], "a regra cumprida (GTIN) não entra")
        self.assertEqual([p["peso"] for p in qualidade["pedidos"]], [analise.MEDIA, analise.ALTA])

    def test_texto_da_nota(self):
        self.assertEqual(analise.texto_qualidade(None), "?")
        self.assertEqual(analise.texto_qualidade(analise.ler_qualidade(None)), "ainda sem nota")
        self.assertEqual(analise.texto_qualidade(analise.ler_qualidade({"score": 74.34})), "74/100")
        self.assertEqual(analise.texto_qualidade(analise.ler_qualidade({"score": 99, "level": "Good"})),
                         "Profissional (99/100)")

    def test_pedido_de_fotos_do_ml_com_outro_nome_nao_repete(self):
        # No primeiro teste real (microfone, 15/10/2026), a regra das fotos veio com outro nome e a sugestão
        # saiu duas vezes: a do Orzy e a do Mercado Livre.
        item = {"title": TITULO_BOM, "pictures": [{"max_size": "1200x1200"}], "shipping": {"free_shipping": False}}
        resposta = performance("MLB1", 88, "Good", "Profissional", [
            ("PICTURES", "QUANTIDADE_DE_FOTOS", "Adicione mais fotos para mostrar seu produto em diferentes "
                                                "ângulos, carregue pelo menos 3"),
            ("free_shipping", "outra_regra", "Ofereça frete grátis")])
        sugestoes = analise.sugerir(item, "POUCA VISITA", None, analise.ler_qualidade(resposta))
        self.assertEqual([s["origem"] for s in sugestoes], ["ML", "ML"])
        self.assertEqual([s["tema"] for s in sugestoes], ["fotos_quantidade", "frete"])
        self.assertEqual(sugestoes[0]["peso"], analise.ALTA, "fica com o peso maior, o da regra do Orzy")

    def test_contar_ficha(self):
        item = {"attributes": self.ficha(BRAND="Genérica", LINE=None)}
        self.assertEqual(analise.contar_ficha(item, ATRIBUTOS_PADRAO), (2, 4))
        self.assertIsNone(analise.contar_ficha(item, None), "sem os campos da categoria, não dá para contar")
        self.assertIsNone(analise.contar_ficha({}, ATRIBUTOS_PADRAO), "sem a ficha do anúncio, também não")
        self.assertEqual(analise.analisar_ficha({}, ATRIBUTOS_PADRAO), [], "e não acusa campo faltando")

    def test_pedido_do_ml_substitui_a_regra_igual_e_fica_com_o_peso_maior(self):
        item = {"title": TITULO_BOM, "pictures": [{"max_size": "1200x1200"}]}
        qualidade = analise.ler_qualidade(performance("MLB1", 50, "Average", "Satisfatória", [
            ("PICTURES", "PICTURES_QUANTITY_MIN", "Adicione mais fotos")]))
        sugestoes = analise.sugerir(item, "POUCA VISITA", None, qualidade)
        self.assertEqual(len(sugestoes), 1)
        self.assertEqual(sugestoes[0]["origem"], "ML")
        self.assertEqual(sugestoes[0]["peso"], analise.ALTA)

    def test_formato_inesperado_nao_derruba_o_relatorio(self):
        # O formato real da nota e de alguns campos ainda vai ser conferido na conta de verdade.
        estranho = {"title": 123, "pictures": ["foto"], "attributes": "x", "shipping": [], "tags": None}
        self.assertEqual(analise.sugerir(estranho, "POUCA VISITA", {"atributos": [1, "a"], "max_titulo": "60"},
                                         analise.ler_qualidade({"buckets": {"a": 1}, "score": "alto"})),
                         [self.sugestao_fotos(1)])
        qualidade = analise.ler_qualidade({"buckets": [{"variables": [{"rules": [{"status": "PENDING",
                                                                                 "wordings": "texto"}]}]}]})
        self.assertEqual(qualidade, {"nota": None, "nivel": None, "pedidos": []})

    def sugestao_fotos(self, tem):
        return analise.analisar_fotos({"pictures": [{}] * tem})[0]

    def test_sugestoes_da_mais_importante_para_a_menos(self):
        item = {"title": "Fone! Pronta Entrega", "pictures": [{"max_size": "500x500"}],
                "shipping": {"free_shipping": False}, "listing_type_id": "gold_special", "attributes": []}
        sugestoes = analise.sugerir(item, "VISITA SEM VENDA", {"atributos": ATRIBUTOS_PADRAO})
        pesos = [s["peso"] for s in sugestoes]
        self.assertEqual(pesos, sorted(pesos, reverse=True))
        self.assertEqual(len(sugestoes), 8)
        self.assertEqual(analise.pontos(sugestoes), sum(pesos))


class TestSemLogin(Base):

    def test_relatorio_antes_de_conectar(self):
        codigo, saida = self.rodar_relatorio()
        self.assertEqual(codigo, 1)
        self.assertIn("Rode primeiro: python conectar.py", saida)


# ================================================================ como a pessoa usa

# Roda o conectar.py de verdade, mas sem abrir o navegador: o "clique em Permitir" é feito pelo simulado.
CONECTAR_SEM_NAVEGADOR = ("import runpy, webbrowser; webbrowser.open = lambda *a, **k: True; "
                          "runpy.run_path('conectar.py', run_name='__main__')")


class TestComoNoPrompt(unittest.TestCase):
    """Roda os dois programas de verdade, como no Prompt de Comando, numa cópia da pasta."""

    def setUp(self):
        self.ml = MLSimulado(client_id=CLIENT_ID, client_secret=SECRET)
        self.ml.adicionar_item("MLB100", "Fone sem fio", preco=99.9, visitas=500)
        self.ml.adicionar_item("MLB200", "Suporte veicular", preco=49.9, visitas=200)
        self.ml.adicionar_pedido("MLB200", quantidade=10)
        base = self.ml.iniciar()
        self.addCleanup(self.ml.parar)

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.pasta = Path(temp.name) / "painel-ml"
        shutil.copytree(PASTA_PAINEL, self.pasta, ignore=shutil.ignore_patterns(
            "__pycache__", "config.json", "tokens.json", "relatorio_anuncios*.csv"))
        self.env = dict(os.environ, ML_API_BASE=base, ML_AUTH_URL=base + "/authorization",
                        PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")

    def test_conectar_e_gerar_relatorio(self):
        proc = subprocess.Popen([sys.executable, "-c", CONECTAR_SEM_NAVEGADOR], cwd=self.pasta, env=self.env,
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8")
        relogio = threading.Timer(60, proc.kill)
        relogio.start()
        self.addCleanup(relogio.cancel)

        proc.stdin.write(f"{CLIENT_ID}\n{SECRET}\n\nn\n")
        proc.stdin.flush()
        saida = []
        link = None
        for linha in proc.stdout:
            saida.append(linha)
            achado = re.search(r"(https?://\S+/authorization\?\S+)", linha)
            if achado:
                link = achado.group(1)
                break
        self.assertIsNotNone(link, "".join(saida))
        proc.stdin.write(self.ml.autorizar(link) + "\n")
        proc.stdin.close()
        saida.append(proc.stdout.read())
        proc.stdout.close()
        proc.wait()
        saida = "".join(saida)
        self.assertEqual(proc.returncode, 0, saida)
        self.assertIn("Pronto! Conectado como LOJA_TESTE", saida)
        self.assertTrue((self.pasta / "config.json").exists())
        self.assertTrue((self.pasta / "tokens.json").exists())

        rel = subprocess.run([sys.executable, "meus_anuncios.py", "--dias", "30"], cwd=self.pasta, env=self.env,
                             capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(rel.returncode, 0, rel.stdout + rel.stderr)
        self.assertIn("Comece por estes", rel.stdout)
        self.assertIn("Título curto", rel.stdout)
        with open(self.pasta / "relatorio_anuncios.csv", encoding="utf-8-sig", newline="") as f:
            linhas = list(csv.DictReader(f, delimiter=";"))
        self.assertEqual([l["situacao"] for l in linhas], ["VISITA SEM VENDA", "VENDENDO BEM"])
        self.assertTrue(all(l["o_que_mudar"] and l["qualidade_ml"] for l in linhas))


if __name__ == "__main__":
    unittest.main()
