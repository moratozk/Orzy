"""Configuração do site, lida das variáveis de ambiente.

O Client Secret do app do Mercado Livre fica só no ambiente do servidor: nunca no código, nunca no GitHub.
"""

import os
from dataclasses import dataclass
from urllib.parse import urlsplit


class ErroConfiguracao(Exception):
    """Falta algo para ligar o site. A mensagem diz o que falta."""


@dataclass(frozen=True)
class Configuracao:
    client_id: str
    client_secret: str
    url_base: str  # endereço público do site, sem barra no final
    banco: str  # arquivo SQLite do histórico
    host: str
    porta: int
    max_anuncios: int  # quantos anúncios um relatório lê, no máximo
    horas_sessao: int  # a sessão some depois de tanto tempo sem uso
    historico: str = "sqlite"  # onde fica o histórico: "sqlite" (arquivo) ou "firestore" (Google Cloud)
    firestore_projeto: str = ""  # id do projeto no Google Cloud, quando o histórico fica no Firestore
    firestore_url: str = ""  # só para o emulador do Firestore; vazio é o Firestore de verdade
    contas_admin: frozenset = frozenset()  # números das contas do Mercado Livre que abrem a página /contagens

    @property
    def redirect_uri(self):
        return self.url_base + "/retorno"

    @property
    def origem(self):
        partes = urlsplit(self.url_base)
        return f"{partes.scheme}://{partes.netloc}"

    @property
    def seguro(self):
        return self.url_base.startswith("https://")

    def app_ml(self):
        """O que o ml_api precisa para falar com o app: id, segredo e Redirect URI."""
        return {"client_id": self.client_id, "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri}


def carregar(ambiente=None):
    env = os.environ if ambiente is None else ambiente
    obrigatorias = ("ORZY_ML_CLIENT_ID", "ORZY_ML_CLIENT_SECRET", "ORZY_URL_BASE")
    faltando = [nome for nome in obrigatorias if not env.get(nome)]
    if faltando:
        raise ErroConfiguracao("faltam estas variáveis de ambiente: " + ", ".join(faltando))

    url_base = env["ORZY_URL_BASE"].strip().rstrip("/")
    # http só para testar no próprio computador (o Mercado Livre não aceita endereço local de verdade).
    if not url_base.startswith(("https://", "http://127.0.0.1")):
        raise ErroConfiguracao("ORZY_URL_BASE precisa começar com https:// "
                               "(para testar aqui, use http://127.0.0.1 com a porta)")

    historico = (env.get("ORZY_HISTORICO") or "sqlite").strip().lower()
    if historico not in ("sqlite", "firestore"):
        raise ErroConfiguracao("ORZY_HISTORICO precisa ser sqlite ou firestore")
    if historico == "firestore" and not env.get("ORZY_FIRESTORE_PROJETO", "").strip():
        raise ErroConfiguracao("com ORZY_HISTORICO=firestore, falta ORZY_FIRESTORE_PROJETO "
                               "(o id do projeto no Google Cloud)")
    admin = [pedaco.strip() for pedaco in env.get("ORZY_CONTAS_ADMIN", "").split(",") if pedaco.strip()]
    if not all(pedaco.isascii() and pedaco.isdigit() for pedaco in admin):
        raise ErroConfiguracao("ORZY_CONTAS_ADMIN precisa ter só o número da conta do Mercado Livre (o ID que o "
                               "conectar.py mostra); para mais de uma conta, separe com vírgula")

    return Configuracao(
        client_id=env["ORZY_ML_CLIENT_ID"],
        client_secret=env["ORZY_ML_CLIENT_SECRET"],
        url_base=url_base,
        banco=env.get("ORZY_BANCO", "orzy.db"),
        host=env.get("ORZY_HOST", "127.0.0.1"),
        porta=int(env.get("PORT") or env.get("ORZY_PORTA") or 8000),
        max_anuncios=int(env.get("ORZY_MAX_ANUNCIOS") or 300),
        horas_sessao=int(env.get("ORZY_HORAS_SESSAO") or 8),
        historico=historico,
        firestore_projeto=env.get("ORZY_FIRESTORE_PROJETO", "").strip(),
        firestore_url=env.get("ORZY_FIRESTORE_URL", "").strip(),
        contas_admin=frozenset(int(pedaco) for pedaco in admin),
    )
