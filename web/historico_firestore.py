"""Histórico dos relatórios no Firestore (Google Cloud), para quando o site rodar no Cloud Run.

O disco do Cloud Run apaga a cada reinício, então lá o histórico não pode ficar num arquivo SQLite. Este arquivo guarda
o mesmo que historico.py (só número, título e números de cada anúncio; nada de token nem de comprador) e responde do
mesmo jeito, então o resto do site não muda. Liga com ORZY_HISTORICO=firestore (ver web/LEIA-ME.md).

Só biblioteca padrão: fala com a API REST do Firestore. O login vem do servidor de metadados do Cloud Run (a conta de
serviço do próprio serviço), sem chave guardada em arquivo.

Cada relatório é um documento da coleção "relatorios", com os anúncios dentro. O número do documento é o momento em
que ele foi criado, em microssegundos: cresce com o tempo, como o número do SQLite. As buscas usam só um campo de cada
vez ou só igualdades, então não pedem índice composto. O campo expira_em é para a política de TTL do Firestore apagar
sozinho o que passou do prazo; o servidor também apaga uma vez por dia (apagar_antigos).
"""

import json
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import analise

from .historico import COLUNAS_ANUNCIO, DIAS_DE_HISTORICO

URL_FIRESTORE = "https://firestore.googleapis.com/v1"
URL_TOKEN = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
COLECAO = "relatorios"
POR_COMMIT = 500  # o Firestore aceita até 500 escritas por commit
TEMPO_MAXIMO = 20  # segundos por chamada
MAX_LISTA = 100  # o mesmo limite do SQLite


class ErroFirestore(Exception):
    """O Firestore recusou ou não respondeu. status: o código HTTP, quando houve resposta."""

    def __init__(self, mensagem, status=None):
        super().__init__(mensagem)
        self.status = status


class TokenDoMetadata:
    """Token da conta de serviço do Cloud Run, pedido ao servidor de metadados e reaproveitado até perto de vencer."""

    def __init__(self, url=URL_TOKEN, agora=time.monotonic):
        self._url = url
        self._agora = agora
        self._token = None
        self._vence = 0.0
        self._trava = threading.Lock()
        # O servidor de metadados fica dentro do Google: nunca passa por proxy.
        self._abrir = urllib.request.build_opener(urllib.request.ProxyHandler({})).open

    def __call__(self):
        with self._trava:
            if self._token is None or self._agora() >= self._vence - 60:
                pedido = urllib.request.Request(self._url, headers={"Metadata-Flavor": "Google"})
                with self._abrir(pedido, timeout=TEMPO_MAXIMO) as resposta:
                    dados = json.load(resposta)
                self._token = dados["access_token"]
                self._vence = self._agora() + int(dados.get("expires_in") or 0)
            return self._token


def _valor(v):
    """Python para o formato de valor da API REST do Firestore."""
    if v is None:
        return {"nullValue": None}
    if isinstance(v, bool):
        return {"booleanValue": v}
    if isinstance(v, int):
        return {"integerValue": str(v)}
    if isinstance(v, float):
        return {"doubleValue": v}
    if isinstance(v, datetime):
        return {"timestampValue": v.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if isinstance(v, str):
        return {"stringValue": v}
    if isinstance(v, dict):
        return {"mapValue": {"fields": {k: _valor(x) for k, x in v.items()}}}
    if isinstance(v, (list, tuple)):
        return {"arrayValue": {"values": [_valor(x) for x in v]}}
    raise TypeError(f"tipo que o histórico não guarda: {type(v).__name__}")


def _do_valor(v):
    """O contrário de _valor. Datas voltam como texto ISO em UTC, igual ao SQLite."""
    (tipo, x), = v.items()
    if tipo == "nullValue":
        return None
    if tipo == "integerValue":
        return int(x)
    if tipo == "timestampValue":
        # O Firestore manda "2026-10-15T18:00:00Z", às vezes com fração de segundo; o Python 3.10 não lê o "Z".
        data = datetime.strptime(x[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return data.isoformat(timespec="seconds")
    if tipo == "mapValue":
        return {k: _do_valor(y) for k, y in (x.get("fields") or {}).items()}
    if tipo == "arrayValue":
        return [_do_valor(y) for y in (x.get("values") or [])]
    return x  # stringValue, booleanValue, doubleValue


def _campos(documento):
    return {k: _do_valor(v) for k, v in (documento.get("fields") or {}).items()}


def _numero(documento):
    return int(documento["name"].rsplit("/", 1)[1])


def _filtro(campo, operacao, valor):
    return {"fieldFilter": {"field": {"fieldPath": campo}, "op": operacao, "value": _valor(valor)}}


def _e(*filtros):
    return {"compositeFilter": {"op": "AND", "filters": list(filtros)}}


class HistoricoFirestore:
    """Mesmas funções de historico.Historico, guardando no Firestore."""

    def __init__(self, projeto, banco="(default)", url=URL_FIRESTORE, token=None, agora=None,
                 dias_guardar=DIAS_DE_HISTORICO):
        self._base = f"{url.rstrip('/')}/projects/{projeto}/databases/{banco}/documents"
        self._token = token if token is not None else TokenDoMetadata()
        self._agora = agora or (lambda: datetime.now(timezone.utc))
        self._dias_guardar = dias_guardar

    def _pedir(self, metodo, caminho, corpo=None):
        """Chama a API. Devolve o JSON da resposta, ou None quando o documento não existe."""
        cabecalhos = {"Content-Type": "application/json"}
        try:
            token = self._token()
        except (urllib.error.URLError, OSError, KeyError, ValueError) as e:
            raise ErroFirestore(f"não consegui o login no servidor de metadados ({type(e).__name__})") from None
        if token:  # o emulador do Firestore não pede login
            cabecalhos["Authorization"] = f"Bearer {token}"
        dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
        pedido = urllib.request.Request(self._base + caminho, data=dados, headers=cabecalhos, method=metodo)
        try:
            with urllib.request.urlopen(pedido, timeout=TEMPO_MAXIMO) as resposta:
                return json.load(resposta)
        except urllib.error.HTTPError as e:
            if e.code == 404 and metodo == "GET":
                return None
            # Só o código e o tipo do erro: a resposta pode repetir dados do pedido.
            try:
                motivo = json.loads(e.read().decode("utf-8"))["error"]["status"]
            except Exception:
                motivo = ""
            raise ErroFirestore(f"o Firestore respondeu {e.code} {motivo}".strip(), e.code) from None
        except (urllib.error.URLError, OSError) as e:
            raise ErroFirestore(f"não consegui falar com o Firestore ({type(e).__name__})") from None

    def _buscar(self, filtro, campos):
        """Documentos da coleção que passam no filtro, só com os campos pedidos ("__name__" para só o nome)."""
        consulta = {"from": [{"collectionId": COLECAO}], "where": filtro,
                    "select": {"fields": [{"fieldPath": c} for c in campos]}}
        resposta = self._pedir("POST", ":runQuery", {"structuredQuery": consulta}) or []
        return [r["document"] for r in resposta if "document" in r]

    def _apagar_documentos(self, documentos):
        nomes = [d["name"] for d in documentos]
        for inicio in range(0, len(nomes), POR_COMMIT):
            self._pedir("POST", ":commit", {"writes": [{"delete": n} for n in nomes[inicio:inicio + POR_COMMIT]]})
        return len(nomes)

    @staticmethod
    def _cabecalho(documento):
        campos = _campos(documento)
        resumo = campos.get("resumo") or {}
        return {"id": _numero(documento), "criado_em": campos["criado_em"], "dias": campos["dias"],
                "total": campos["total"],
                # O Firestore não guarda a ordem das chaves: volta na ordem das situações, como no SQLite.
                "resumo": {s: resumo.get(s, 0) for s in analise.ORDEM}}

    def salvar(self, ml_user_id, dias, linhas):
        agora = self._agora()
        campos = {
            "ml_user_id": int(ml_user_id),
            "criado_em": agora,
            "expira_em": agora + timedelta(days=self._dias_guardar),  # para a política de TTL do Firestore
            "dias": dias,
            "total": len(linhas),
            "resumo": {s: sum(1 for l in linhas if l["situacao"] == s) for s in analise.ORDEM},
            "anuncios": [{"id": l["id"], "titulo": l["titulo"], "visitas": l["visitas"], "vendas": l["vendas"],
                          "situacao": l["situacao"], "pontos": l["pontos"]} for l in linhas],
        }
        corpo = {"fields": {k: _valor(v) for k, v in campos.items()}}
        id_ = int(agora.timestamp()) * 1_000_000 + agora.microsecond
        for _ in range(5):  # dois relatórios no mesmo microssegundo: o segundo pega o número seguinte
            try:
                self._pedir("POST", f"/{COLECAO}?documentId={id_}", corpo)
                return id_
            except ErroFirestore as e:
                if e.status != 409:
                    raise
                id_ += 1
        raise ErroFirestore("não achei um número livre para o relatório")

    def listar(self, ml_user_id):
        documentos = self._buscar(_filtro("ml_user_id", "EQUAL", int(ml_user_id)),
                                  ("criado_em", "dias", "total", "resumo"))
        return sorted((self._cabecalho(d) for d in documentos), key=lambda r: r["id"], reverse=True)[:MAX_LISTA]

    def ver(self, ml_user_id, relatorio_id):
        """Um relatório guardado, só se for da conta pedida. Devolve None se não for."""
        documento = self._pedir("GET", f"/{COLECAO}/{int(relatorio_id)}")
        if documento is None:
            return None
        campos = _campos(documento)
        if campos.get("ml_user_id") != int(ml_user_id):
            return None
        dados = self._cabecalho(documento)
        dados["anuncios"] = [{c: a.get(c) for c in COLUNAS_ANUNCIO} for a in campos.get("anuncios") or []]
        return dados

    def id_do_anterior(self, ml_user_id, relatorio_id):
        """O relatório guardado logo antes deste, da mesma conta e do mesmo período. Devolve o número ou None."""
        este = self._pedir("GET", f"/{COLECAO}/{int(relatorio_id)}?mask.fieldPaths=ml_user_id&mask.fieldPaths=dias")
        if este is None:
            return None
        campos = _campos(este)
        if campos.get("ml_user_id") != int(ml_user_id):
            return None
        mesmos = self._buscar(_e(_filtro("ml_user_id", "EQUAL", int(ml_user_id)),
                                 _filtro("dias", "EQUAL", campos["dias"])), ("__name__",))
        return max((n for n in map(_numero, mesmos) if n < int(relatorio_id)), default=None)

    def apagar(self, ml_user_id):
        """Apaga todos os relatórios da conta. Devolve quantos foram apagados."""
        return self._apagar_documentos(self._buscar(_filtro("ml_user_id", "EQUAL", int(ml_user_id)), ("__name__",)))

    def apagar_antigos(self, dias):
        limite = self._agora() - timedelta(days=dias)
        return self._apagar_documentos(self._buscar(_filtro("criado_em", "LESS_THAN", limite), ("__name__",)))
