"""Sessões do site, guardadas só na memória do servidor.

O token de acesso do Mercado Livre fica aqui: nunca vai para o navegador nem para arquivo.
Se o servidor reiniciar, todo mundo conecta de novo. Por isso o site roda com uma instância só.

Uma sessão com login acaba `horas` depois do login, mesmo em uso: é o prazo do cookie, e a Política de Privacidade
promete apagar o login, o apelido e os relatórios da memória no máximo 8 horas depois de a pessoa entrar.
"""

import secrets
import threading
import time
from dataclasses import dataclass, field

MINUTOS_LOGIN_PENDENTE = 15  # quem clicou em Conectar e não voltou do Mercado Livre
MAX_LOGIN_PENDENTE = 1000  # robôs que só abrem /entrar não enchem a memória do servidor


@dataclass
class Sessao:
    id: str
    ultimo_uso: float
    login_pendente: dict | None = None  # estado e verificador do PKCE, até o Mercado Livre devolver a pessoa
    cliente: object | None = None  # ClienteDaSessao, com o token de acesso
    usuario: dict | None = None  # {"id", "apelido"} da conta conectada
    relatorios: dict = field(default_factory=dict)  # id do relatório -> Relatorio
    login_em: float | None = None  # quando o login terminou: o prazo da sessão conta daqui


class Sessoes:
    def __init__(self, horas=8, agora=time.time, minutos_pendente=MINUTOS_LOGIN_PENDENTE,
                 max_pendentes=MAX_LOGIN_PENDENTE):
        self._horas = horas
        self._minutos_pendente = minutos_pendente
        self._max_pendentes = max_pendentes
        self._agora = agora
        self._dados = {}
        self._trava = threading.Lock()

    def criar(self):
        with self._trava:
            self._limpar()
            # No limite, sai a sessão sem login mais antiga. Sessões com login não contam.
            pendentes = sorted((s for s in self._dados.values() if s.cliente is None), key=lambda s: s.ultimo_uso)
            for velha in pendentes[:max(0, len(pendentes) - self._max_pendentes + 1)]:
                del self._dados[velha.id]
            sessao = Sessao(id=secrets.token_urlsafe(32), ultimo_uso=self._agora())
            self._dados[sessao.id] = sessao
            return sessao

    def trocar_id(self, id_):
        """Dá um código novo à sessão depois do login (o código de antes do login deixa de valer) e marca a hora do
        login, de onde conta o prazo da sessão."""
        with self._trava:
            sessao = self._dados.pop(id_, None)
            if sessao is not None:
                sessao.id = secrets.token_urlsafe(32)
                sessao.login_em = self._agora()
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

    def limpar(self, antecedencia=0):
        """Apaga as sessões vencidas sem esperar o próximo pedido, e também as que vencem nos próximos `antecedencia`
        segundos: quem limpa a cada minuto passa 60, e nenhuma sessão fica na memória além do prazo."""
        with self._trava:
            self._limpar(antecedencia)

    def _limpar(self, antecedencia=0):
        momento = self._agora() + antecedencia
        com_login, sem_login = momento - self._horas * 3600, momento - self._minutos_pendente * 60
        for id_ in [i for i, s in self._dados.items()
                    if self._comeco(s) < (com_login if s.cliente is not None else sem_login)]:
            del self._dados[id_]

    @staticmethod
    def _comeco(sessao):
        """De onde conta o prazo: o login, para quem entrou (usar o site não estica); o último uso, para quem não
        voltou do Mercado Livre. Entre o fim do login e a troca do código, ainda não há hora do login: vale o uso."""
        if sessao.cliente is not None and sessao.login_em is not None:
            return sessao.login_em
        return sessao.ultimo_uso
