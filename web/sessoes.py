"""Sessões do site, guardadas só na memória do servidor.

O token de acesso do Mercado Livre fica aqui: nunca vai para o navegador nem para arquivo.
Se o servidor reiniciar, todo mundo conecta de novo. Por isso o site roda com uma instância só.
"""

import secrets
import threading
import time
from dataclasses import dataclass, field


@dataclass
class Sessao:
    id: str
    ultimo_uso: float
    login_pendente: dict | None = None  # estado e verificador do PKCE, até o Mercado Livre devolver a pessoa
    cliente: object | None = None  # ClienteDaSessao, com o token de acesso
    usuario: dict | None = None  # {"id", "apelido"} da conta conectada
    relatorios: dict = field(default_factory=dict)  # id do relatório -> Relatorio


class Sessoes:
    def __init__(self, horas=8, agora=time.time):
        self._horas = horas
        self._agora = agora
        self._dados = {}
        self._trava = threading.Lock()

    def criar(self):
        with self._trava:
            self._limpar()
            sessao = Sessao(id=secrets.token_urlsafe(32), ultimo_uso=self._agora())
            self._dados[sessao.id] = sessao
            return sessao

    def obter(self, id_):
        with self._trava:
            self._limpar()
            sessao = self._dados.get(id_)
            if sessao is not None:
                sessao.ultimo_uso = self._agora()
            return sessao

    def encerrar(self, id_):
        with self._trava:
            self._dados.pop(id_, None)

    def _limpar(self):
        limite = self._agora() - self._horas * 3600
        for id_ in [i for i, s in self._dados.items() if s.ultimo_uso < limite]:
            del self._dados[id_]
