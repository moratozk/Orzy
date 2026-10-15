"""Rotas do site. Cada requisição vira (status, cabeçalhos, corpo); o servidor só repassa a resposta."""

import json
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import meus_anuncios
from . import login, paginas
from .historico import Historico
from .relatorios import ERRO, GERANDO, PRONTO, ErroRelatorio, Relatorios
from .sessoes import Sessoes

NOME_COOKIE = "orzy_sessao"
OPCOES_DIAS = (30, 60, 90, 150)
PASTA_STATIC = Path(__file__).resolve().parent / "static"
ARQUIVOS_STATIC = {"estilo.css": "text/css; charset=utf-8",
                   "andamento.js": "application/javascript; charset=utf-8"}

CABECALHOS_DE_SEGURANCA = [
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),  # o código do Mercado Livre não pode vazar para outros sites
    ("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                                "form-action 'self'; frame-ancestors 'none'; base-uri 'none'"),
]


class Site:
    def __init__(self, config, historico=None, sessoes=None, relatorios=None):
        self.config = config
        self.historico = historico or Historico(config.banco)
        self.sessoes = sessoes or Sessoes(horas=config.horas_sessao)
        self.relatorios = relatorios or Relatorios(self.historico, config.max_anuncios)

    def tratar(self, metodo, endereco, cabecalhos, corpo=b""):
        status, extras, dados = self._rotear(metodo, urlsplit(endereco), cabecalhos, corpo)
        return status, extras + CABECALHOS_DE_SEGURANCA, dados

    # ------------------------------------------------------------ rotas

    def _rotear(self, metodo, url, cabecalhos, corpo):
        caminho = url.path
        fixas = {
            ("GET", "/"): lambda: self._inicio(cabecalhos),
            ("GET", "/entrar"): self._entrar,
            ("GET", "/retorno"): lambda: self._retorno(cabecalhos, url.query),
            ("GET", "/relatorio"): lambda: self._formulario(cabecalhos),
            ("POST", "/relatorio/gerar"): lambda: self._gerar(cabecalhos, corpo),
            ("GET", "/historico"): lambda: self._historico(cabecalhos),
            ("POST", "/historico/apagar"): lambda: self._apagar_historico(cabecalhos, corpo),
            ("POST", "/sair"): lambda: self._sair(cabecalhos),
            ("GET", "/privacidade"): self._privacidade,
            ("GET", "/saude"): self._saude,
        }
        rota = fixas.get((metodo, caminho))
        if rota is not None:
            return rota()
        partes = caminho.split("/")  # "/relatorio/ID/csv" vira ["", "relatorio", "ID", "csv"]
        if metodo == "GET" and len(partes) == 3:
            if partes[1] == "static":
                return self._arquivo(partes[2])
            if partes[1] == "relatorio":
                return self._ver_relatorio(partes[2], cabecalhos)
            if partes[1] == "historico":
                return self._ver_historico(partes[2], cabecalhos)
        if metodo == "GET" and len(partes) == 4 and partes[1] == "relatorio":
            if partes[3] == "andamento.json":
                return self._andamento(partes[2], cabecalhos)
            if partes[3] == "csv":
                return self._csv(partes[2], cabecalhos)
        return self._nao_encontrado()

    # ------------------------------------------------------------ entrada e login

    def _inicio(self, cabecalhos):
        return self._html(200, paginas.inicio(self._logada(cabecalhos) is not None))

    def _entrar(self):
        sessao = self.sessoes.criar()
        destino = login.iniciar(self.config, sessao)
        return self._redirect(destino, extras=[self._cookie(sessao.id, self.config.horas_sessao * 3600)])

    def _retorno(self, cabecalhos, consulta):
        sessao = self._sessao(cabecalhos)
        if sessao is None:
            return self._html(400, paginas.erro("Sua sessão expirou. Clique em Conectar de novo para entrar."))
        parametros = {chave: valores[0] for chave, valores in parse_qs(consulta).items()}
        try:
            sessao.cliente, sessao.usuario = login.concluir(self.config, sessao, parametros)
        except login.ErroLoginSite as e:
            return self._html(400, paginas.erro(str(e)))
        return self._redirect("/relatorio")

    def _sair(self, cabecalhos):
        if not self._origem_ok(cabecalhos):
            return self._recusado()
        sessao = self._sessao(cabecalhos)
        if sessao is not None:
            self.sessoes.encerrar(sessao.id)
        return self._redirect("/", extras=[self._cookie("", 0)])

    # ------------------------------------------------------------ relatórios

    def _formulario(self, cabecalhos):
        sessao = self._logada(cabecalhos)
        if sessao is None:
            return self._redirect("/")
        return self._html(200, paginas.formulario(sessao.usuario, OPCOES_DIAS,
                                                  em_andamento=self._em_andamento(sessao)))

    def _gerar(self, cabecalhos, corpo):
        sessao = self._logada(cabecalhos)
        if sessao is None:
            return self._redirect("/")
        if not self._origem_ok(cabecalhos):
            return self._recusado()
        try:
            relatorio = self.relatorios.iniciar(sessao, sessao.cliente, self._dias(corpo))
        except ErroRelatorio as e:
            return self._html(200, paginas.formulario(sessao.usuario, OPCOES_DIAS, aviso=str(e)))
        return self._redirect(f"/relatorio/{relatorio.id}", status=303)

    def _ver_relatorio(self, relatorio_id, cabecalhos):
        relatorio = self._relatorio_da_sessao(relatorio_id, cabecalhos)
        if relatorio is None:
            return self._nao_encontrado()
        if relatorio.estado == GERANDO:
            return self._html(200, paginas.andamento(relatorio))
        if relatorio.estado == ERRO:
            return self._html(200, paginas.relatorio_com_erro(relatorio))
        return self._html(200, paginas.resultado(relatorio))

    def _andamento(self, relatorio_id, cabecalhos):
        relatorio = self._relatorio_da_sessao(relatorio_id, cabecalhos)
        if relatorio is None:
            return self._nao_encontrado()
        dados = json.dumps(relatorio.para_json(), ensure_ascii=False).encode("utf-8")
        return 200, [("Content-Type", "application/json; charset=utf-8"), ("Cache-Control", "no-store")], dados

    def _csv(self, relatorio_id, cabecalhos):
        relatorio = self._relatorio_da_sessao(relatorio_id, cabecalhos)
        if relatorio is None or relatorio.estado != PRONTO:
            return self._nao_encontrado()
        texto = meus_anuncios.montar_csv(relatorio.linhas, relatorio.dias)
        return 200, [("Content-Type", "text/csv; charset=utf-8"),
                     ("Content-Disposition", f'attachment; filename="orzy-anuncios-{relatorio.dias}-dias.csv"'),
                     ("Cache-Control", "no-store")], ("﻿" + texto).encode("utf-8")

    # ------------------------------------------------------------ histórico

    def _historico(self, cabecalhos):
        sessao = self._logada(cabecalhos)
        if sessao is None:
            return self._redirect("/")
        return self._html(200, paginas.historico(self.historico.listar(sessao.usuario["id"])))

    def _ver_historico(self, relatorio_id, cabecalhos):
        sessao = self._logada(cabecalhos)
        if sessao is None:
            return self._redirect("/")
        if not relatorio_id.isdigit():
            return self._nao_encontrado()
        dados = self.historico.ver(sessao.usuario["id"], int(relatorio_id))
        if dados is None:
            return self._nao_encontrado()
        return self._html(200, paginas.historico_relatorio(dados))

    def _apagar_historico(self, cabecalhos, corpo):
        sessao = self._logada(cabecalhos)
        if sessao is None:
            return self._redirect("/")
        if not self._origem_ok(cabecalhos):
            return self._recusado()
        if "on" not in parse_qs(corpo.decode("utf-8", "replace")).get("confirmo", []):
            return self._html(400, paginas.erro("Confirme que quer apagar o histórico."))
        self.historico.apagar(sessao.usuario["id"])
        # Tira da sessão os relatórios já prontos; um que ainda está sendo gerado continua até terminar.
        sessao.relatorios = {i: r for i, r in sessao.relatorios.items() if r.estado == GERANDO}
        return self._redirect("/historico", status=303)

    # ------------------------------------------------------------ páginas simples

    def _privacidade(self):
        return self._html(200, paginas.privacidade())

    def _saude(self):
        return 200, [("Content-Type", "text/plain; charset=utf-8"), ("Cache-Control", "no-store")], b"ok"

    def _arquivo(self, nome):
        tipo = ARQUIVOS_STATIC.get(nome)
        if tipo is None:
            return self._nao_encontrado()
        return 200, [("Content-Type", tipo), ("Cache-Control", "public, max-age=3600")], \
            (PASTA_STATIC / nome).read_bytes()

    def _nao_encontrado(self):
        return self._html(404, paginas.erro("Não encontrei essa página."))

    def _recusado(self):
        return self._html(403, paginas.erro("Pedido recusado. Volte à página e tente de novo."))

    # ------------------------------------------------------------ ajudantes

    @staticmethod
    def _html(status, html, extras=()):
        return status, [("Content-Type", "text/html; charset=utf-8"), ("Cache-Control", "no-store"),
                        *extras], html.encode("utf-8")

    @staticmethod
    def _redirect(destino, status=302, extras=()):
        return status, [("Location", destino), ("Cache-Control", "no-store"), *extras], b""

    def _cookie(self, valor, duracao):
        atributos = [f"{NOME_COOKIE}={valor}", "Path=/", "HttpOnly", "SameSite=Lax", f"Max-Age={duracao}"]
        if self.config.seguro:
            atributos.append("Secure")
        return "Set-Cookie", "; ".join(atributos)

    def _sessao(self, cabecalhos):
        try:
            cookies = SimpleCookie(cabecalhos.get("Cookie") or "")
        except CookieError:
            return None
        morsel = cookies.get(NOME_COOKIE)
        return self.sessoes.obter(morsel.value) if morsel is not None else None

    def _logada(self, cabecalhos):
        """A sessão, se a pessoa já concluiu o login com o Mercado Livre; senão None."""
        sessao = self._sessao(cabecalhos)
        return sessao if sessao is not None and sessao.cliente is not None else None

    def _relatorio_da_sessao(self, relatorio_id, cabecalhos):
        sessao = self._logada(cabecalhos)
        return sessao.relatorios.get(relatorio_id) if sessao is not None else None

    @staticmethod
    def _em_andamento(sessao):
        return next((r for r in sessao.relatorios.values() if r.estado == GERANDO), None)

    def _origem_ok(self, cabecalhos):
        # Pedidos que mudam algo só valem se vierem do próprio site (proteção contra pedidos de outros sites).
        return cabecalhos.get("Origin") == self.config.origem

    @staticmethod
    def _dias(corpo):
        try:
            dias = int(parse_qs(corpo.decode("utf-8", "replace")).get("dias", ["30"])[0])
        except ValueError:
            return OPCOES_DIAS[0]
        return dias if dias in OPCOES_DIAS else OPCOES_DIAS[0]
