"""
Conexão com a API do Mercado Livre (Brasil).

Guarda os dados do app em config.json e o login em tokens.json,
na mesma pasta deste arquivo. NÃO compartilhe esses dois arquivos.

Só usa a biblioteca padrão do Python: não precisa instalar nada.
"""

import base64
import hashlib
import http.client
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ARQ_CONFIG = PASTA / "config.json"
ARQ_TOKENS = PASTA / "tokens.json"

AUTH_URL = os.environ.get("ML_AUTH_URL", "https://auth.mercadolivre.com.br/authorization")
API_BASE = os.environ.get("ML_API_BASE", "https://api.mercadolibre.com").rstrip("/")

# O Mercado Livre não aceita "localhost" como Redirect URI. Usamos uma página pública
# qualquer: depois do login, o código aparece no endereço e você copia de lá.
REDIRECT_PADRAO = "https://www.google.com"

USER_AGENT = "PainelAnunciosML/1.0"
MARGEM_RENOVACAO = 300  # renova o token 5 minutos antes de vencer
VALIDADE_PADRAO = 21600  # 6 horas, caso a resposta não informe


class ErroML(Exception):
    """Erro vindo da API do Mercado Livre, já com mensagem em português."""

    def __init__(self, mensagem, status=None, codigo=None):
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo


class ErroLogin(ErroML):
    """O login venceu, foi cancelado ou ainda não foi feito: precisa rodar conectar.py."""


class ErroColagem(ErroML):
    """O que foi colado não tem o código, mas o login ainda espera: dá para colar de novo."""


# ---------------------------------------------------------------- arquivos

def _ler_json(caminho):
    if not caminho.exists():
        return None
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _gravar_json(caminho, dados):
    # Grava num arquivo temporário e só troca no final. Se o PC desligar no meio,
    # o arquivo antigo continua inteiro (o refresh token só pode ser usado uma vez,
    # então perder o novo obrigaria a fazer login de novo).
    temp = caminho.with_name(caminho.name + ".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(temp, caminho)


def carregar_config():
    return _ler_json(ARQ_CONFIG)


def salvar_config(config):
    _gravar_json(ARQ_CONFIG, config)


def carregar_tokens():
    return _ler_json(ARQ_TOKENS)


def salvar_tokens(tokens):
    _gravar_json(ARQ_TOKENS, tokens)


# ---------------------------------------------------------------- HTTP

def _requisicao(metodo, url, cabecalhos=None, corpo=None, tentativas=4):
    """Faz a chamada e devolve o JSON. Tenta de novo se bater no limite (429) ou em instabilidade."""
    cab = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if cabecalhos:
        cab.update(cabecalhos)
    dados = None
    if corpo is not None:
        dados = urllib.parse.urlencode(corpo).encode("utf-8")
        cab["Content-Type"] = "application/x-www-form-urlencoded"

    espera = 2
    for tentativa in range(1, tentativas + 1):
        req = urllib.request.Request(url, data=dados, headers=cab, method=metodo)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                texto = resp.read().decode("utf-8", errors="replace")
            return _decodificar(texto)
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", errors="replace")
            try:
                erro = json.loads(texto)
            except ValueError:
                erro = None
            if not isinstance(erro, dict):
                erro = {"message": texto[:300]}
            if e.code in (429, 500, 502, 503, 504) and tentativa < tentativas:
                time.sleep(espera)
                espera *= 2
                continue
            mensagem = erro.get("message") or erro.get("error") or f"HTTP {e.code}"
            raise ErroML(mensagem, status=e.code, codigo=erro.get("error")) from None
        except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
            # Sem internet, conexão caiu no meio da resposta ou demorou demais.
            if tentativa < tentativas:
                time.sleep(espera)
                espera *= 2
                continue
            motivo = getattr(e, "reason", None) or e
            raise ErroML(f"Sem conexão com o Mercado Livre ({motivo}). Verifique sua internet.") from None


def _decodificar(texto):
    if not texto.strip():
        return None
    try:
        return json.loads(texto)
    except ValueError:
        # Acontece em rede com bloqueio (escola, trabalho), que devolve uma página no lugar dos dados.
        raise ErroML("O Mercado Livre respondeu algo inesperado, que não veio em formato de dados. "
                     "Se você estiver numa rede com bloqueio, como a da escola ou do trabalho, "
                     "tente de outra internet.") from None


# ---------------------------------------------------------------- login (OAuth)

def gerar_pkce():
    """Gera o par do PKCE: o verifier fica no seu PC, o challenge vai no link de login."""
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def montar_url_autorizacao(config, state, challenge=None):
    params = {
        "response_type": "code",
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "state": state,
    }
    if challenge:
        params["code_challenge"] = challenge
        params["code_challenge_method"] = "S256"
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


def extrair_code(texto, state_esperado=None):
    """Aceita o endereço inteiro copiado do navegador ou só o código TG-..."""
    texto = texto.strip().strip('"').strip("'")
    if not texto:
        raise ErroColagem("Nada foi colado.")
    if "code=" in texto or "error=" in texto or texto.lower().startswith("http"):
        if not texto.lower().startswith("http"):
            texto = "https://" + texto
        params = urllib.parse.parse_qs(urllib.parse.urlparse(texto).query)
        if "error" in params:
            detalhe = params.get("error_description", params["error"])[0]
            raise ErroML("O Mercado Livre recusou a autorização: " + detalhe)
        if "code" not in params:
            raise ErroColagem("Não achei o código (code=...) nesse endereço. Copie o endereço INTEIRO "
                         "da barra do navegador, logo depois de clicar em Permitir.")
        state = params.get("state", [None])[0]
        if state_esperado and state is not None and state != state_esperado:
            raise ErroML("Esse endereço é de outra tentativa de login. "
                         "Rode python conectar.py de novo e use o link novo.")
        return params["code"][0]
    return texto


def _explicar_erro_token(erro, na_troca):
    codigo = (erro.codigo or "").lower()
    texto = str(erro).lower()
    if codigo == "invalid_client":
        return ("Client ID ou Client Secret incorretos. Confira no app do Mercado Livre e rode: "
                "python conectar.py --refazer")
    if "code_verifier" in texto or "code_challenge" in texto or "pkce" in texto:
        return ("Problema com o PKCE: a resposta sobre o PKCE precisa bater com o que está no app. "
                "Rode python conectar.py --refazer e responda de acordo.")
    if codigo == "invalid_grant":
        if na_troca:
            return ("O código não foi aceito. Ele vale poucos minutos, só pode ser usado uma vez, "
                    "e a Redirect URI precisa ser idêntica à cadastrada no app. "
                    "Rode python conectar.py e tente de novo.")
        return "Seu login venceu ou foi cancelado. Entre de novo com: python conectar.py"
    return f"Erro ao obter o token: {erro}"


def montar_tokens(resposta, anterior=None):
    """Monta o login a partir da resposta do Mercado Livre. Não grava nada no disco."""
    anterior = anterior or {}
    return {
        "access_token": resposta["access_token"],
        "refresh_token": resposta.get("refresh_token") or anterior.get("refresh_token"),
        "user_id": resposta.get("user_id") or anterior.get("user_id"),
        "scope": resposta.get("scope") or anterior.get("scope"),
        "expira_em": time.time() + int(resposta.get("expires_in") or VALIDADE_PADRAO),
    }


def _guardar_resposta_token(resposta, anterior=None):
    tokens = montar_tokens(resposta, anterior)
    salvar_tokens(tokens)
    return tokens


def _pedir_token(corpo, na_troca):
    try:
        return _requisicao("POST", API_BASE + "/oauth/token", corpo=corpo)
    except ErroML as e:
        raise ErroLogin(_explicar_erro_token(e, na_troca=na_troca), e.status, e.codigo) from None


def trocar_code_por_token(config, code, verifier=None, gravar=True):
    corpo = {
        "grant_type": "authorization_code",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": code,
        "redirect_uri": config["redirect_uri"],
    }
    if verifier:
        corpo["code_verifier"] = verifier
    resposta = _pedir_token(corpo, na_troca=True)
    return _guardar_resposta_token(resposta) if gravar else montar_tokens(resposta)


def renovar_token(config, tokens, gravar=True):
    if not tokens.get("refresh_token"):
        raise ErroLogin("Seu login não se renova sozinho (falta marcar 'Refresh Token' em Fluxos OAuth, no app). "
                        "Marque essa opção e rode: python conectar.py")
    corpo = {
        "grant_type": "refresh_token",
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "refresh_token": tokens["refresh_token"],
    }
    resposta = _pedir_token(corpo, na_troca=False)
    if gravar:
        return _guardar_resposta_token(resposta, anterior=tokens)
    return montar_tokens(resposta, anterior=tokens)


# ---------------------------------------------------------------- cliente

class ClienteML:
    """Chamadas à API com o login já carregado. Quem guarda o login (arquivo ou memória) decide o resto."""

    _mensagem_login = "O Mercado Livre recusou seu login. Entre de novo."

    def __init__(self, config, tokens):
        self.config = config
        self.tokens = tokens

    def _renovar(self):
        # Não grava: quem quiser gravar o login renovado sobrescreve este método (ver MercadoLivre).
        return renovar_token(self.config, self.tokens, gravar=False)

    def _guardar(self):
        """Grava o login depois de mudar. Aqui não grava nada."""

    def _access_token(self):
        if time.time() > self.tokens.get("expira_em", 0) - MARGEM_RENOVACAO:
            self.tokens = self._renovar()
        return self.tokens["access_token"]

    def get(self, caminho, params=None):
        url = API_BASE + caminho
        if params:
            url += "?" + urllib.parse.urlencode(params, safe=",")
        for tentativa in range(2):
            cab = {"Authorization": "Bearer " + self._access_token()}
            try:
                return _requisicao("GET", url, cabecalhos=cab)
            except ErroML as e:
                if e.status == 401 and tentativa == 0:
                    # Token recusado antes da hora (ex.: senha trocada). Renova e tenta uma vez.
                    self.tokens = self._renovar()
                    continue
                if e.status == 401:
                    raise ErroLogin(self._mensagem_login, 401, e.codigo) from None
                if e.status == 403:
                    raise ErroML(f"Sem permissão ({e}). Confira se você entrou com a conta dona "
                                 "dos anúncios, e não com um operador, e se o seu app no Mercado Livre "
                                 "tem permissão de leitura para anúncios, vendas e métricas.",
                                 403, e.codigo) from None
                raise

    def obter_usuario(self):
        """Dados da conta conectada (id, apelido). Também confirma que o login funciona."""
        eu = self.get("/users/me")
        if eu and eu.get("id") and self.tokens.get("user_id") != eu["id"]:
            self.tokens["user_id"] = eu["id"]
            self._guardar()
        return eu


class MercadoLivre(ClienteML):
    """Cliente do PC: lê config.json e tokens.json e grava o login renovado na mesma pasta."""

    _mensagem_login = "O Mercado Livre recusou seu login. Entre de novo com: python conectar.py"

    def __init__(self):
        config, tokens = carregar_config(), carregar_tokens()
        if not config or not tokens:
            raise ErroLogin("Você ainda não conectou sua conta. Rode primeiro: python conectar.py")
        super().__init__(config, tokens)

    def _renovar(self):
        return renovar_token(self.config, self.tokens)

    def _guardar(self):
        salvar_tokens(self.tokens)
