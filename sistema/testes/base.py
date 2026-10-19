"""O que os testes das páginas usam: a configuração de teste, o navegador, o Mercado Livre simulado e o login
inteiro."""

import tempfile
from pathlib import Path
from unittest import mock

import ml_api
from contas import cofre
from contas.models import Conta
from contas.sessoes import GUARDADAS
from django.conf import settings
from django.test import Client, TransactionTestCase, override_settings
from ml_simulado import MLSimulado, performance
from orzy.configuracao import Configuracao
from relatorios import datas

URL = "https://orzy.test"
CLIENT_ID = "1234567890"
SECRET = "segredo-de-teste"
CONTA = 111222333
CHAVE = bytes(range(32))  # a chave do acesso guardado nos testes (no servidor, vem de ORZY_CHAVE_ACESSO)
TITULO_BOM = "Fone de Ouvido Bluetooth Sem Fio Marca Teste Modelo X1 Preto"
LINHA = {"id": "MLB9", "titulo": "Anúncio de outra conta", "visitas": 1, "vendas": 0, "situacao": "POUCA VISITA",
         "pontos": 0}


def criar_conta(ml_user_id, apelido="", **campos):
    """Uma conta guardada sem passar pelo Conectar e sem acesso guardado (para o histórico de outra conta, por
    exemplo)."""
    agora = datas.agora()
    return Conta.objects.create(**{"ml_user_id": ml_user_id, "apelido": apelido, "criada_em": agora,
                                   "conectada_em": agora, **campos})


def codigo_guardado(ml_user_id=CONTA):
    """O código de renovação guardado da conta, aberto com a chave dos testes."""
    return cofre.abrir(CHAVE, ml_user_id, Conta.objects.get(ml_user_id=ml_user_id).acesso)


def com_configuracao(**extra):
    """override_settings com a configuração dos testes e o que o settings.py tira dela. Os testes não dependem das
    variáveis de ambiente, só do banco (ORZY_BANCO_URL)."""
    config = Configuracao(**{"client_id": CLIENT_ID, "client_secret": SECRET, "url_base": URL,
                             "banco": settings.ORZY.banco, "chave_acesso": CHAVE, **extra})
    return override_settings(ORZY=config, ALLOWED_HOSTS=[config.host], CSRF_TRUSTED_ORIGINS=[config.origem],
                             SESSION_COOKIE_SECURE=config.seguro, SESSION_COOKIE_AGE=config.horas_sessao * 3600)


class Navegador(Client):
    """Um navegador falando com https://orzy.test, com a conferência de pedidos de outros sites (CSRF) ligada, como no
    site de verdade (o Client do Django desliga por padrão)."""

    def __init__(self):
        super().__init__(enforce_csrf_checks=True, HTTP_HOST="orzy.test")


@com_configuracao()
class SistemaBase(TransactionTestCase):
    """Uma pessoa num navegador, o Mercado Livre simulado e o sistema com o banco de teste.

    TransactionTestCase porque o relatório roda numa thread com a própria conexão ao banco.
    """

    client_class = Navegador

    def setUp(self):
        self.ml = MLSimulado(client_id=CLIENT_ID, client_secret=SECRET, redirect_uri=URL + "/retorno",
                             user_id=CONTA, nickname="LOJA_TESTE")
        base = self.ml.iniciar()
        self.addCleanup(self.ml.parar)

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.pasta = Path(temp.name)
        # Aponta o sistema para o simulado. Nada pode ser gravado na pasta do programa do PC.
        for trocar in (mock.patch.object(ml_api, "API_BASE", base),
                       mock.patch.object(ml_api, "AUTH_URL", base + "/authorization"),
                       mock.patch.object(ml_api, "ARQ_CONFIG", self.pasta / "config.json"),
                       mock.patch.object(ml_api, "ARQ_TOKENS", self.pasta / "tokens.json")):
            trocar.start()
            self.addCleanup(trocar.stop)

        # As sessões ficam na memória do processo: cada teste começa sem nenhuma.
        GUARDADAS._dados.clear()
        self.addCleanup(GUARDADAS._dados.clear)

    # ------------------------------------------------------------ pedidos

    def abrir(self, caminho, cliente=None, **extra):
        """GET por https, como o navegador."""
        return (cliente or self.client).get(caminho, secure=True, **extra)

    def enviar(self, caminho, dados=None, origem=URL, com_codigo=True, cliente=None):
        """POST de um formulário do site: com a origem e o código que o {% csrf_token %} põe no formulário."""
        cliente = cliente or self.client
        dados = dict(dados or {})
        if com_codigo:
            dados["csrfmiddlewaretoken"] = self.sessao(cliente).get("_csrftoken", "")
        return cliente.post(caminho, dados, secure=True, headers={"Origin": origem} if origem else {})

    @staticmethod
    def texto(resposta):
        return resposta.content.decode("utf-8")

    def sessao(self, cliente=None):
        """A sessão deste navegador como o servidor guarda (o mesmo dicionário), ou {} se não houver."""
        cookie = (cliente or self.client).cookies.get("orzy_sessao")
        return (GUARDADAS.obter(cookie.value) if cookie else None) or {}

    # ------------------------------------------------------------ login e relatório

    def semear(self):
        self.ml.adicionar_item("MLB1000000001", TITULO_BOM, preco=79.9, estoque=10, visitas=0)
        self.ml.adicionar_item("MLB1000000002", "<script>alert(1)</script> Caixa de som", visitas=120)
        self.ml.adicionar_pedido("MLB1000000002", quantidade=2, dias_atras=3)
        self.ml.qualidade["MLB1000000002"] = performance("MLB1000000002", 88, "Good", "Profissional")

    def entrar(self, cliente=None):
        """O login inteiro: /entrar, o clique em Permitir no simulado e a volta para /retorno."""
        resposta = self.abrir("/entrar", cliente)
        self.assertEqual(resposta.status_code, 302)
        endereco = self.ml.autorizar(resposta["Location"])
        resposta = self.abrir(endereco[len(URL):], cliente)
        self.assertEqual((resposta.status_code, resposta.get("Location")), (302, "/relatorio"),
                         "o retorno deveria levar para /relatorio")
        return resposta

    def entrar_sem_mercado_livre(self, usuario, cliente=None):
        """Uma sessão com login pronta, sem passar pelo Mercado Livre (para outra conta, por exemplo)."""
        cliente = cliente or self.client
        chave = "sessao-" + str(usuario["id"])
        GUARDADAS.criar(chave, {"cliente": object(), "usuario": usuario, "relatorios": {},
                                "login_em": GUARDADAS.agora()})
        cliente.cookies["orzy_sessao"] = chave
        return cliente

    def gerar(self, dias=30):
        resposta = self.enviar("/relatorio/gerar", {"dias": dias})
        self.assertEqual(resposta.status_code, 303)
        return resposta["Location"].rsplit("/", 1)[1]

    def esperar(self, relatorio_id):
        relatorio = self.sessao()["relatorios"][relatorio_id]
        relatorio.thread.join(timeout=30)
        self.assertFalse(relatorio.thread.is_alive(), "o relatório demorou demais")
        return relatorio

    def chamadas_de_token(self):
        return [c for c in self.ml.chamadas if c[0] == "POST" and c[1] == "/oauth/token"]
