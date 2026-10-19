"""Configuração do sistema, lida das variáveis de ambiente.

O Client Secret do app do Mercado Livre e a senha do banco ficam só no ambiente do servidor: nunca no código, nunca no
GitHub.
"""

import os
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, unquote, urlsplit

OBRIGATORIAS = ("ORZY_ML_CLIENT_ID", "ORZY_ML_CLIENT_SECRET", "ORZY_URL_BASE", "ORZY_BANCO_URL")
MAX_HORAS_SESSAO = 8  # a Política de Privacidade promete: o login sai da memória no máximo 8 horas depois da entrada


class ErroConfiguracao(Exception):
    """Falta algo para ligar o sistema. A mensagem diz o que falta."""


@dataclass(frozen=True)
class Configuracao:
    client_id: str
    client_secret: str
    url_base: str  # endereço público do site, sem barra no final
    banco: dict = field(repr=False)  # a conexão com o PostgreSQL, no formato do Django (tem a senha: fora do repr)
    max_anuncios: int = 300  # quantos anúncios um relatório lê, no máximo
    horas_sessao: int = 8  # a sessão com login acaba tanto tempo depois do login, mesmo em uso (o prazo do cookie)
    contas_admin: frozenset = frozenset()  # números das contas do Mercado Livre que abrem a página /contagens

    @property
    def redirect_uri(self):
        return self.url_base + "/retorno"

    @property
    def origem(self):
        partes = urlsplit(self.url_base)
        return f"{partes.scheme}://{partes.netloc}"

    @property
    def host(self):
        return urlsplit(self.url_base).hostname

    @property
    def seguro(self):
        return self.url_base.startswith("https://")

    def app_ml(self):
        """O que o ml_api precisa para falar com o app: id, segredo e Redirect URI."""
        return {"client_id": self.client_id, "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri}


def ler_banco(url):
    """ORZY_BANCO_URL (postgresql://usuário:senha@servidor:porta/banco?sslmode=require) no formato do Django."""
    partes = urlsplit(url.strip())
    try:
        porta = partes.port
    except ValueError:
        porta = -1
    if partes.scheme not in ("postgres", "postgresql") or not partes.hostname or not partes.path.strip("/") \
            or porta == -1:
        raise ErroConfiguracao("ORZY_BANCO_URL precisa ser um endereço postgresql://usuário:senha@servidor/banco")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(partes.path.strip("/")),
        "USER": unquote(partes.username or ""),
        "PASSWORD": unquote(partes.password or ""),
        "HOST": partes.hostname,
        "PORT": str(porta or ""),
        "OPTIONS": dict(parse_qsl(partes.query)),  # sslmode=require, por exemplo
    }


def _inteiro(env, nome, padrao, minimo, maximo):
    texto = (env.get(nome) or "").strip()
    if not texto:
        return padrao
    if not (texto.isascii() and texto.isdigit()) or not minimo <= int(texto) <= maximo:
        raise ErroConfiguracao(f"{nome} precisa ser um número de {minimo} a {maximo}")
    return int(texto)


def carregar(ambiente=None):
    env = os.environ if ambiente is None else ambiente
    faltando = [nome for nome in OBRIGATORIAS if not env.get(nome)]
    if faltando:
        raise ErroConfiguracao("faltam estas variáveis de ambiente: " + ", ".join(faltando))

    url_base = env["ORZY_URL_BASE"].strip().rstrip("/")
    partes = urlsplit(url_base)
    # http só para testar no próprio computador (o Mercado Livre não aceita endereço local de verdade).
    if not partes.hostname or not (partes.scheme == "https" or
                                   (partes.scheme == "http" and partes.hostname == "127.0.0.1")):
        raise ErroConfiguracao("ORZY_URL_BASE precisa começar com https:// "
                               "(para testar aqui, use http://127.0.0.1 com a porta)")

    admin = [pedaco.strip() for pedaco in env.get("ORZY_CONTAS_ADMIN", "").split(",") if pedaco.strip()]
    if not all(pedaco.isascii() and pedaco.isdigit() for pedaco in admin):
        raise ErroConfiguracao("ORZY_CONTAS_ADMIN precisa ter só o número da conta do Mercado Livre (o ID que o "
                               "conectar.py mostra); para mais de uma conta, separe com vírgula")

    return Configuracao(
        client_id=env["ORZY_ML_CLIENT_ID"],
        client_secret=env["ORZY_ML_CLIENT_SECRET"],
        url_base=url_base,
        banco=ler_banco(env["ORZY_BANCO_URL"]),
        max_anuncios=_inteiro(env, "ORZY_MAX_ANUNCIOS", 300, 1, 10_000),
        horas_sessao=_inteiro(env, "ORZY_HORAS_SESSAO", 8, 1, MAX_HORAS_SESSAO),
        contas_admin=frozenset(int(pedaco) for pedaco in admin),
    )
