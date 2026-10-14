"""
Mercado Livre simulado, para testar o painel sem usar a sua conta de verdade.

Imita só o pedaço da API que o painel usa:
  - login (OAuth, com PKCE opcional e refresh token de uso único)
  - /users/me
  - busca dos seus anúncios, inclusive o modo "scan" (acima de 1000 anúncios)
  - multiget de no máximo 20 anúncios por chamada
  - visitas por anúncio
  - busca de pedidos pagos
Também simula os problemas mais comuns: erro 429 (muitas chamadas), login vencido,
falta de permissão e falha numa chamada.

Os formatos seguem a documentação pública do Mercado Livre. Os textos das mensagens
de erro são aproximados: o que importa para os testes são o status HTTP e o campo "error".

Só usa a biblioteca padrão do Python.
"""

import base64
import hashlib
import json
import re
import secrets
import threading
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FORMATO_DATA = "%Y-%m-%dT%H:%M:%S.000-00:00"


class MLSimulado:
    def __init__(self, client_id="1234567890", client_secret="segredo-de-teste",
                 redirect_uri="https://www.google.com", exigir_pkce=False,
                 user_id=111222333, nickname="LOJA_TESTE"):
        self.app = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "exigir_pkce": exigir_pkce,
        }
        self.usuario = {"id": user_id, "nickname": nickname, "site_id": "MLB"}
        self.expires_in = 21600

        self.itens = {}          # id -> dados do anúncio
        self.visitas = {}        # id -> total de visitas no período (ou None para dar erro)
        self.pedidos = []
        self.erros_por_rota = {}  # prefixo da rota -> status HTTP para devolver sempre
        # O que fazer nas próximas chamadas, em ordem: um status HTTP (ex.: 429),
        # "derrubar" (fecha a conexão sem responder) ou "html" (página no lugar dos dados).
        self.falhas = []

        self._codes = {}          # code -> dados da autorização
        self._access = {}         # access token -> expira em (timestamp)
        self._refresh = {}        # refresh token -> True se ainda vale
        self._scrolls = {}        # scroll_id -> posição
        self.chamadas = []        # (método, caminho, parâmetros) de cada chamada recebida
        self._trava = threading.Lock()
        self._servidor = None
        self.base = None

    # ------------------------------------------------------------ dados

    def adicionar_item(self, item_id, titulo, preco=100.0, estoque=10, visitas=0, status="active"):
        self.itens[item_id] = {
            "id": item_id,
            "title": titulo,
            "price": preco,
            "currency_id": "BRL",
            "available_quantity": estoque,
            "status": status,
            "permalink": f"https://produto.mercadolivre.com.br/{item_id[:3]}-{item_id[3:]}-teste",
            "listing_type_id": "gold_special",
            "pictures": [{"id": "1"}],
        }
        self.visitas[item_id] = visitas

    def adicionar_pedido(self, item_id, quantidade=1, dias_atras=1, status="paid", seller_id=None):
        criado = datetime.now(timezone.utc) - timedelta(days=dias_atras)
        self.pedidos.append({
            "id": 2000000000 + len(self.pedidos),
            "status": status,
            "date_created": criado.strftime(FORMATO_DATA),
            "seller": {"id": seller_id or self.usuario["id"]},
            "pack_id": None,
            "order_items": [{
                "item": {"id": item_id, "title": self.itens.get(item_id, {}).get("title", "")},
                "quantity": quantidade,
                "unit_price": self.itens.get(item_id, {}).get("price", 0),
            }],
        })

    # ------------------------------------------------------------ "navegador"

    def autorizar(self, url_autorizacao):
        """Faz o papel do navegador: a pessoa clica em Permitir e o ML manda para a Redirect URI.

        Devolve o endereço que apareceria na barra do navegador.
        """
        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url_autorizacao).query))
        if params.get("client_id") != self.app["client_id"]:
            raise ValueError("client_id desconhecido")
        if params.get("redirect_uri") != self.app["redirect_uri"]:
            raise ValueError("redirect_uri diferente da cadastrada no app")
        if params.get("response_type") != "code":
            raise ValueError("response_type precisa ser code")
        desafio = params.get("code_challenge")
        if self.app["exigir_pkce"] and not desafio:
            raise ValueError("este app exige PKCE e o code_challenge não veio")
        if desafio and params.get("code_challenge_method") not in ("S256", "plain"):
            raise ValueError("code_challenge_method inválido")

        code = "TG-" + secrets.token_hex(12) + "-" + str(self.usuario["id"])
        with self._trava:
            self._codes[code] = {
                "redirect_uri": params["redirect_uri"],
                "desafio": desafio,
                "metodo": params.get("code_challenge_method"),
                "usado": False,
                "expira": time.time() + 600,
            }
        retorno = {"code": code}
        if "state" in params:
            retorno["state"] = params["state"]
        return self.app["redirect_uri"] + "?" + urllib.parse.urlencode(retorno)

    def revogar_access_tokens(self):
        """Como se a pessoa tivesse trocado a senha: os access tokens param de valer na hora."""
        with self._trava:
            self._access.clear()

    def revogar_tudo(self):
        """Como se a pessoa tivesse tirado a permissão do app: nada mais vale."""
        with self._trava:
            self._access.clear()
            self._refresh.clear()

    def refresh_ainda_vale(self, refresh_token):
        return self._refresh.get(refresh_token, False)

    # ------------------------------------------------------------ servidor

    def iniciar(self, porta=0):
        simulado = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                simulado._atender(self, "GET")

            def do_POST(self):
                simulado._atender(self, "POST")

        self._servidor = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
        threading.Thread(target=self._servidor.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self._servidor.server_address[1]}"
        return self.base

    def parar(self):
        if self._servidor:
            self._servidor.shutdown()
            self._servidor.server_close()

    # ------------------------------------------------------------ respostas

    def _atender(self, req, metodo):
        url = urllib.parse.urlparse(req.path)
        params = dict(urllib.parse.parse_qsl(url.query))
        corpo = {}
        if metodo == "POST":
            tamanho = int(req.headers.get("Content-Length") or 0)
            bruto = req.rfile.read(tamanho).decode("utf-8")
            if "application/x-www-form-urlencoded" not in (req.headers.get("Content-Type") or ""):
                return self._erro(req, 400, "invalid_request", "content-type precisa ser x-www-form-urlencoded")
            corpo = dict(urllib.parse.parse_qsl(bruto))
        with self._trava:
            self.chamadas.append((metodo, url.path, params))
            falha = self.falhas.pop(0) if self.falhas else None
        if falha == "derrubar":
            req.close_connection = True
            return None
        if falha == "html":
            texto = "<html><body>Acesso bloqueado pela rede</body></html>".encode("utf-8")
            req.send_response(200)
            req.send_header("Content-Type", "text/html")
            req.send_header("Content-Length", str(len(texto)))
            req.end_headers()
            req.wfile.write(texto)
            return None
        if falha:
            codigo = "local_rate_limited" if falha == 429 else "internal_error"
            return self._erro(req, falha, codigo, "falha simulada")
        for prefixo, status in self.erros_por_rota.items():
            if url.path.startswith(prefixo):
                return self._erro(req, status, "forbidden" if status == 403 else "error", "erro simulado")

        if metodo == "POST" and url.path == "/oauth/token":
            return self._token(req, corpo)
        if metodo != "GET":
            return self._erro(req, 405, "method_not_allowed", "método não suportado")
        if url.path == "/authorization":
            # Para testar à mão no navegador: "clica em Permitir" sozinho e redireciona.
            try:
                destino = self.autorizar(req.path)
            except ValueError as e:
                return self._erro(req, 400, "invalid_request", str(e))
            req.send_response(302)
            req.send_header("Location", destino)
            req.send_header("Content-Length", "0")
            req.end_headers()
            return None

        if not self._token_valido(req):
            return self._erro(req, 401, "unauthorized", "invalid access token")

        caminho = url.path
        if caminho == "/users/me":
            return self._json(req, 200, self.usuario)
        m = re.fullmatch(r"/users/(\d+)/items/search", caminho)
        if m:
            return self._buscar_itens(req, int(m.group(1)), params)
        if caminho == "/items":
            return self._multiget(req, params)
        m = re.fullmatch(r"/items/([A-Z]{3}\d+)/visits/time_window", caminho)
        if m:
            return self._visitas(req, m.group(1), params)
        if caminho == "/orders/search":
            return self._pedidos(req, params)
        return self._erro(req, 404, "not_found", "resource not found")

    def _json(self, req, status, dados):
        texto = json.dumps(dados).encode("utf-8")
        req.send_response(status)
        req.send_header("Content-Type", "application/json;charset=UTF-8")
        req.send_header("Content-Length", str(len(texto)))
        req.end_headers()
        req.wfile.write(texto)

    def _erro(self, req, status, codigo, mensagem):
        return self._json(req, status, {"message": mensagem, "error": codigo, "status": status, "cause": []})

    def _token_valido(self, req):
        cab = req.headers.get("Authorization") or ""
        if not cab.startswith("Bearer "):
            return False
        expira = self._access.get(cab[len("Bearer "):])
        return expira is not None and expira > time.time()

    # ------------------------------------------------------------ OAuth

    def _novo_par(self):
        access = "APP_USR-" + secrets.token_hex(16)
        refresh = "TG-" + secrets.token_hex(16)
        self._access[access] = time.time() + self.expires_in
        self._refresh[refresh] = True
        return {
            "access_token": access,
            "token_type": "Bearer",
            "expires_in": self.expires_in,
            "scope": "offline_access read",
            "user_id": self.usuario["id"],
            "refresh_token": refresh,
        }

    def _token(self, req, corpo):
        if corpo.get("client_id") != self.app["client_id"] or corpo.get("client_secret") != self.app["client_secret"]:
            return self._erro(req, 401, "invalid_client", "invalid client_id or client_secret")
        tipo = corpo.get("grant_type")
        with self._trava:
            if tipo == "authorization_code":
                dados = self._codes.get(corpo.get("code"))
                if (not dados or dados["usado"] or dados["expira"] < time.time()
                        or dados["redirect_uri"] != corpo.get("redirect_uri")):
                    return self._erro(req, 400, "invalid_grant", "Error validating grant. Your authorization "
                                      "code or refresh token may be expired or it was already used")
                if dados["desafio"]:
                    verifier = corpo.get("code_verifier")
                    if not verifier:
                        return self._erro(req, 400, "invalid_request", "code_verifier is required")
                    if dados["metodo"] == "S256":
                        calculado = base64.urlsafe_b64encode(
                            hashlib.sha256(verifier.encode("ascii")).digest()).decode("ascii").rstrip("=")
                    else:
                        calculado = verifier
                    if calculado != dados["desafio"]:
                        return self._erro(req, 400, "invalid_grant", "invalid code_verifier")
                dados["usado"] = True
                return self._json(req, 200, self._novo_par())
            if tipo == "refresh_token":
                atual = corpo.get("refresh_token")
                if not self._refresh.get(atual):
                    return self._erro(req, 400, "invalid_grant", "Error validating grant. Your authorization "
                                      "code or refresh token may be expired or it was already used")
                self._refresh[atual] = False  # uso único
                return self._json(req, 200, self._novo_par())
        return self._erro(req, 400, "unsupported_grant_type", "grant_type inválido")

    # ------------------------------------------------------------ recursos

    def _buscar_itens(self, req, user_id, params):
        if user_id != self.usuario["id"]:
            return self._erro(req, 403, "forbidden", "caller.id does not match")
        status = params.get("status")
        ids = [i for i, d in self.itens.items() if status is None or d["status"] == status]
        limite = int(params.get("limit", 50))
        if limite > 100:
            return self._erro(req, 400, "bad_request", "limit must be lower or equal to 100")

        if params.get("search_type") == "scan":
            scroll = params.get("scroll_id")
            with self._trava:
                if scroll:
                    if scroll not in self._scrolls:
                        return self._erro(req, 400, "bad_request", "invalid scroll_id")
                    inicio = self._scrolls[scroll]
                else:
                    scroll = secrets.token_hex(8)
                    inicio = 0
                self._scrolls[scroll] = inicio + limite
            return self._json(req, 200, {
                "seller_id": str(user_id),
                "results": ids[inicio:inicio + limite],
                "paging": {"total": len(ids), "limit": limite},
                "scroll_id": scroll,
            })

        offset = int(params.get("offset", 0))
        if offset + limite > 1000:
            return self._erro(req, 400, "bad_request",
                              "Invalid limit and offset values. Use search_type=scan for more than 1000 results")
        return self._json(req, 200, {
            "seller_id": str(user_id),
            "results": ids[offset:offset + limite],
            "paging": {"total": len(ids), "offset": offset, "limit": limite},
        })

    def _multiget(self, req, params):
        ids = [i for i in (params.get("ids") or "").split(",") if i]
        if not ids:
            return self._erro(req, 400, "bad_request", "ids is required")
        if len(ids) > 20:
            return self._erro(req, 400, "bad_request", "max 20 ids per request")
        campos = [c for c in (params.get("attributes") or "").split(",") if c]
        resposta = []
        for item_id in ids:
            dados = self.itens.get(item_id)
            if not dados:
                resposta.append({"code": 404, "body": {"message": f"Item with id {item_id} not found",
                                                       "error": "not_found", "status": 404, "cause": []}})
                continue
            corpo = {k: v for k, v in dados.items() if not campos or k in campos}
            resposta.append({"code": 200, "body": corpo})
        return self._json(req, 200, resposta)

    def _visitas(self, req, item_id, params):
        if item_id not in self.itens:
            return self._erro(req, 404, "not_found", "item not found")
        if params.get("unit") != "day" or not (params.get("last") or "").isdigit():
            return self._erro(req, 400, "bad_request", "invalid last/unit")
        total = self.visitas.get(item_id)
        if total is None:
            return self._erro(req, 500, "internal_error", "erro simulado nas visitas")
        fim = datetime.now(timezone.utc)
        inicio = fim - timedelta(days=int(params["last"]))
        return self._json(req, 200, {
            "item_id": item_id,
            "date_from": inicio.strftime("%Y-%m-%dT00:00:00Z"),
            "date_to": fim.strftime("%Y-%m-%dT00:00:00Z"),
            "total_visits": total,
            "last": int(params["last"]),
            "unit": "day",
            "results": [],
        })

    def _pedidos(self, req, params):
        if str(params.get("seller")) != str(self.usuario["id"]):
            return self._erro(req, 403, "forbidden", "caller.id does not match seller")
        limite = int(params.get("limit", 50))
        if limite > 51:
            return self._erro(req, 400, "bad_request", "limit must be lower or equal to 51")
        offset = int(params.get("offset", 0))
        status = set((params.get("order.status") or "").split(",")) - {""}
        de = params.get("order.date_created.from")
        ate = params.get("order.date_created.to")
        de = datetime.strptime(de, "%Y-%m-%dT%H:%M:%S.%f%z") if de else None
        ate = datetime.strptime(ate, "%Y-%m-%dT%H:%M:%S.%f%z") if ate else None

        achados = []
        for p in self.pedidos:
            if p["seller"]["id"] != self.usuario["id"] or p["status"] == "cancelled":
                continue  # vendedor não vê pedidos cancelados na busca
            if status and p["status"] not in status:
                continue
            criado = datetime.strptime(p["date_created"], "%Y-%m-%dT%H:%M:%S.%f%z")
            if (de and criado < de) or (ate and criado > ate):
                continue
            achados.append(p)
        achados.sort(key=lambda p: p["date_created"], reverse=params.get("sort") == "date_desc")
        return self._json(req, 200, {
            "query": None,
            "results": achados[offset:offset + limite],
            "paging": {"total": len(achados), "offset": offset, "limit": limite},
            "sort": {"id": params.get("sort", "date_asc")},
        })


if __name__ == "__main__":
    # Para testar à mão: suba o simulado numa janela e, em outra, aponte o painel para ele:
    #   set ML_API_BASE=http://127.0.0.1:8765
    #   set ML_AUTH_URL=http://127.0.0.1:8765/authorization
    #   python conectar.py --refazer    (Client ID 1234567890, Secret segredo-de-teste)
    ml = MLSimulado()
    ml.adicionar_item("MLB1000000001", "Produto de teste que vende", preco=59.9, visitas=120)
    ml.adicionar_item("MLB1000000002", "Produto de teste parado", preco=89.9, visitas=300)
    ml.adicionar_pedido("MLB1000000001", quantidade=2)
    print("Mercado Livre simulado rodando em", ml.iniciar(porta=8765))
    print("Ctrl+C para parar.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ml.parar()
