"""Firestore e servidor de metadados do Google, simulados, para testar web/historico_firestore.py sem conta e sem
internet. Só biblioteca padrão, como o resto.

Imita o pedaço da API REST v1 que o site usa: criar documento (com documentId), ler (com mask), runQuery (fieldFilter
EQUAL e LESS_THAN, compositeFilter AND, select e limit) e commit (delete, e update com updateMask e increment). Como o
Firestore de verdade, pede o token que o servidor de metadados entregou, recusa criar um documento que já existe,
aceita até 500 escritas por commit, aplica o commit inteiro ou nada e, num update sem updateMask, troca o documento
inteiro. orderBy fica de fora de propósito: junto de um filtro em outro campo, o Firestore pediria um índice composto.
"""

import json
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

CAMINHO_TOKEN = "/computeMetadata/v1/instance/service-accounts/default/token"
TIPOS = {"nullValue", "booleanValue", "integerValue", "doubleValue", "timestampValue", "stringValue", "mapValue",
         "arrayValue"}
DATA_RFC3339 = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,9})?Z$")
TAMANHO_MAXIMO = 1_048_576  # 1 MiB por documento
CAMPO_SIMPLES = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")  # caminho de campo que não precisa de crase


class ErroAPI(Exception):
    def __init__(self, codigo, status, mensagem=""):
        super().__init__(mensagem or status)
        self.codigo, self.status = codigo, status


def _agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _conferir_valor(valor):
    """Recusa o que o Firestore recusaria: tipo desconhecido, inteiro fora do formato de texto, data inválida."""
    if not isinstance(valor, dict) or len(valor) != 1 or next(iter(valor)) not in TIPOS:
        raise ErroAPI(400, "INVALID_ARGUMENT", f"valor inválido: {valor!r}")
    (tipo, x), = valor.items()
    if tipo == "integerValue" and not (isinstance(x, str) and re.fullmatch(r"-?\d+", x)):
        raise ErroAPI(400, "INVALID_ARGUMENT", f"integerValue precisa ser texto: {x!r}")
    if tipo == "timestampValue" and not (isinstance(x, str) and DATA_RFC3339.match(x)):
        raise ErroAPI(400, "INVALID_ARGUMENT", f"timestampValue inválido: {x!r}")
    if tipo == "mapValue":
        for v in (x.get("fields") or {}).values():
            _conferir_valor(v)
    if tipo == "arrayValue":
        for v in x.get("values") or []:
            _conferir_valor(v)


def _como_guardado(valor):
    """Como o Firestore devolve um valor: campos de mapa em ordem alfabética (a ordem da escrita não volta) e
    lista ou mapa vazio sem a chave de dentro."""
    if "mapValue" in valor:
        campos = valor["mapValue"].get("fields") or {}
        return {"mapValue": {"fields": _campos_guardados(campos)}} if campos else {"mapValue": {}}
    if "arrayValue" in valor:
        itens = valor["arrayValue"].get("values") or []
        return {"arrayValue": {"values": [_como_guardado(v) for v in itens]}} if itens else {"arrayValue": {}}
    return valor


def _campos_guardados(campos):
    return {nome: _como_guardado(campos[nome]) for nome in sorted(campos)}


def _ordenavel(valor):
    """(tipo, valor) para comparar: o Firestore só compara valores do mesmo tipo nos filtros de faixa."""
    (tipo, x), = valor.items()
    if tipo == "integerValue":
        return ("numero", int(x))
    if tipo == "doubleValue":
        return ("numero", float(x))
    if tipo == "timestampValue":
        return ("data", datetime.strptime(x[:19], "%Y-%m-%dT%H:%M:%S"))
    return (tipo, json.dumps(x, sort_keys=True))


def _passa(documento, filtro):
    if "compositeFilter" in filtro:
        composto = filtro["compositeFilter"]
        if composto.get("op") != "AND":
            raise ErroAPI(400, "INVALID_ARGUMENT", "só AND é simulado")
        return all(_passa(documento, f) for f in composto["filters"])
    campo = filtro["fieldFilter"]
    valor = (documento.get("fields") or {}).get(campo["field"]["fieldPath"])
    if valor is None:
        return False  # documento sem o campo não entra
    _conferir_valor(campo["value"])
    a, b = _ordenavel(valor), _ordenavel(campo["value"])
    if campo["op"] == "EQUAL":
        return a == b
    if campo["op"] == "LESS_THAN":
        return a[0] == b[0] and a[1] < b[1]
    raise ErroAPI(400, "INVALID_ARGUMENT", f"operação não simulada: {campo['op']}")


def _so_campos(documento, caminhos):
    if caminhos is None:
        return documento
    copia = {k: v for k, v in documento.items() if k != "fields"}
    campos = {c: documento["fields"][c] for c in caminhos if c != "__name__" and c in documento.get("fields", {})}
    if campos:
        copia["fields"] = campos
    return copia


class FirestoreSimulado:
    def __init__(self, projeto="orzy-teste", banco="(default)"):
        self.projeto = projeto
        self.banco = banco
        self.documentos = {}  # nome completo -> documento, como a API devolve
        self.tokens = set()
        self.tokens_entregues = 0
        self.chamadas = []  # (método, caminho sem a busca)
        self.falhar = []  # códigos HTTP para as próximas chamadas ao Firestore (ex.: [503])
        self.max_escritas = 500  # por commit, como o Firestore; um teste pode baixar para não criar 501 documentos
        self._trava = threading.Lock()
        self._servidor = None

    @property
    def prefixo(self):
        return f"projects/{self.projeto}/databases/{self.banco}/documents"

    # ------------------------------------------------------------ ligar e desligar

    def iniciar(self):
        simulado = self

        class Manipulador(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                simulado._atender(self, "GET")

            def do_POST(self):
                simulado._atender(self, "POST")

        self._servidor = ThreadingHTTPServer(("127.0.0.1", 0), Manipulador)
        threading.Thread(target=self._servidor.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{self._servidor.server_address[1]}"
        self.url_firestore = base + "/v1"
        self.url_token = base + CAMINHO_TOKEN
        return base

    def parar(self):
        self._servidor.shutdown()
        self._servidor.server_close()

    # ------------------------------------------------------------ pedidos

    def _atender(self, pedido, metodo):
        url = urlsplit(pedido.path)
        tamanho = int(pedido.headers.get("Content-Length") or 0)
        corpo = json.loads(pedido.rfile.read(tamanho) or b"null") if tamanho else None
        try:
            with self._trava:
                self.chamadas.append((metodo, url.path))
                resposta = self._rotear(metodo, url, pedido.headers, corpo)
            codigo = 200
        except ErroAPI as e:
            codigo, resposta = e.codigo, {"error": {"code": e.codigo, "status": e.status, "message": str(e)}}
        dados = json.dumps(resposta).encode("utf-8")
        pedido.send_response(codigo)
        pedido.send_header("Content-Type", "application/json; charset=utf-8")
        pedido.send_header("Content-Length", str(len(dados)))
        pedido.end_headers()
        pedido.wfile.write(dados)

    def _rotear(self, metodo, url, cabecalhos, corpo):
        if url.path == CAMINHO_TOKEN:
            if cabecalhos.get("Metadata-Flavor") != "Google":
                raise ErroAPI(403, "FORBIDDEN", "falta o cabeçalho Metadata-Flavor")
            self.tokens_entregues += 1
            token = f"token-{self.tokens_entregues}"
            self.tokens.add(token)
            return {"access_token": token, "expires_in": 3599, "token_type": "Bearer"}

        if cabecalhos.get("Authorization", "").removeprefix("Bearer ") not in self.tokens:
            raise ErroAPI(401, "UNAUTHENTICATED", "token ausente ou inválido")
        if self.falhar:
            raise ErroAPI(self.falhar.pop(0), "UNAVAILABLE")

        raiz = "/v1/" + self.prefixo
        if metodo == "POST" and url.path == raiz + ":runQuery":
            return self._consultar(corpo["structuredQuery"])
        if metodo == "POST" and url.path == raiz + ":commit":
            return self._commit(corpo["writes"])
        if not url.path.startswith(raiz + "/"):
            raise ErroAPI(404, "NOT_FOUND")
        partes = url.path[len(raiz) + 1:].split("/")
        busca = parse_qs(url.query)
        if metodo == "POST" and len(partes) == 1:
            return self._criar(partes[0], busca["documentId"][0], corpo)
        if metodo == "GET" and len(partes) == 2:
            return self._ler(f"{self.prefixo}/{partes[0]}/{partes[1]}", busca.get("mask.fieldPaths"))
        raise ErroAPI(404, "NOT_FOUND")

    def _criar(self, colecao, id_, corpo):
        nome = f"{self.prefixo}/{colecao}/{id_}"
        if nome in self.documentos:
            raise ErroAPI(409, "ALREADY_EXISTS", "o documento já existe")
        for valor in corpo["fields"].values():
            _conferir_valor(valor)
        if len(json.dumps(corpo)) > TAMANHO_MAXIMO:
            raise ErroAPI(400, "INVALID_ARGUMENT", "documento maior que 1 MiB")
        agora = _agora()
        self.documentos[nome] = {"name": nome, "fields": _campos_guardados(corpo["fields"]), "createTime": agora,
                                 "updateTime": agora}
        return self.documentos[nome]

    def _ler(self, nome, caminhos):
        if nome not in self.documentos:
            raise ErroAPI(404, "NOT_FOUND", "documento não encontrado")
        return _so_campos(self.documentos[nome], caminhos)

    def _consultar(self, consulta):
        if "orderBy" in consulta:
            raise ErroAPI(400, "FAILED_PRECONDITION", "orderBy não simulado: com filtro em outro campo, pede índice")
        colecao = consulta["from"][0]["collectionId"]
        caminhos = [c["fieldPath"] for c in consulta["select"]["fields"]] if "select" in consulta else None
        achados = [d for nome, d in sorted(self.documentos.items())
                   if nome.startswith(f"{self.prefixo}/{colecao}/")
                   and ("where" not in consulta or _passa(d, consulta["where"]))]
        if "limit" in consulta:
            achados = achados[:int(consulta["limit"])]
        agora = _agora()
        if not achados:
            return [{"readTime": agora}]  # como o Firestore: sem documento, só a hora da leitura
        return [{"document": _so_campos(d, caminhos), "readTime": agora} for d in achados]

    def _commit(self, escritas):
        if len(escritas) > self.max_escritas:
            raise ErroAPI(400, "INVALID_ARGUMENT", f"mais de {self.max_escritas} escritas num commit")
        for escrita in escritas:  # confere tudo antes de mudar algo: o commit vale inteiro ou nada
            self._conferir_escrita(escrita)
        for escrita in escritas:
            if "delete" in escrita:
                self.documentos.pop(escrita["delete"], None)  # apagar o que não existe não é erro
            else:
                self._atualizar(escrita)
        return {"writeResults": [{} for _ in escritas], "commitTime": _agora()}

    def _conferir_escrita(self, escrita):
        if set(escrita) == {"delete"}:
            return
        if "update" not in escrita or not set(escrita) <= {"update", "updateMask", "updateTransforms"}:
            raise ErroAPI(400, "INVALID_ARGUMENT", f"escrita não simulada: {sorted(escrita)}")
        nome = escrita["update"]["name"]
        if not nome.startswith(self.prefixo + "/") or len(nome[len(self.prefixo) + 1:].split("/")) != 2:
            raise ErroAPI(400, "INVALID_ARGUMENT", f"nome de documento inválido: {nome}")
        for valor in (escrita["update"].get("fields") or {}).values():
            _conferir_valor(valor)
        for transformacao in escrita.get("updateTransforms") or []:
            if set(transformacao) != {"fieldPath", "increment"}:
                raise ErroAPI(400, "INVALID_ARGUMENT", "só increment é simulado")
            if not CAMPO_SIMPLES.fullmatch(transformacao["fieldPath"]):
                raise ErroAPI(400, "INVALID_ARGUMENT", f"caminho de campo não simulado: {transformacao['fieldPath']}")
            _conferir_valor(transformacao["increment"])
            if "integerValue" not in transformacao["increment"]:
                raise ErroAPI(400, "INVALID_ARGUMENT", "só increment de inteiro é simulado")

    def _atualizar(self, escrita):
        """update: sem updateMask, o documento inteiro vira o que veio; com ele, só os campos da máscara mudam (os da
        máscara que não vieram somem). Depois, cada increment soma no campo (campo que não existe vira o valor)."""
        nome = escrita["update"]["name"]
        novos = escrita["update"].get("fields") or {}
        agora = _agora()
        documento = self.documentos.get(nome) or {"name": nome, "createTime": agora}
        if "updateMask" in escrita:
            campos = dict(documento.get("fields") or {})
            for caminho in escrita["updateMask"].get("fieldPaths") or []:
                if caminho in novos:
                    campos[caminho] = novos[caminho]
                else:
                    campos.pop(caminho, None)
        else:
            campos = dict(novos)
        for transformacao in escrita.get("updateTransforms") or []:
            atual = campos.get(transformacao["fieldPath"]) or {}
            if "doubleValue" in atual:
                raise ErroAPI(400, "INVALID_ARGUMENT", "increment em campo double não é simulado")
            soma = int(transformacao["increment"]["integerValue"]) + int(atual.get("integerValue", 0))
            campos[transformacao["fieldPath"]] = {"integerValue": str(soma)}
        documento.update({"fields": _campos_guardados(campos), "updateTime": agora})
        self.documentos[nome] = documento
