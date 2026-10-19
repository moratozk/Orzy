"""Sessões do sistema, guardadas só na memória do servidor (o SESSION_ENGINE do Django aponta para cá).

O token de acesso do Mercado Livre fica aqui: nunca vai para o navegador, para arquivo ou para o banco (o código que o
renova fica no banco, cifrado: ver acesso.py). Se o servidor reiniciar, todo mundo conecta de novo. Por isso o sistema
roda com um processo só (ver gunicorn.conf.py).

Uma sessão com login acaba `horas` depois do login, mesmo em uso: é o prazo do cookie, e a Política de Privacidade
promete apagar o login, o apelido e os relatórios da memória no máximo 8 horas depois de a pessoa entrar. Quem clicou
em Conectar e não voltou do Mercado Livre sai em 15 minutos sem uso.

Os dados de cada sessão ficam aqui como estão, sem virar texto: o cliente do Mercado Livre e os relatórios em
andamento são objetos que o Django nunca grava.
"""

import threading
import time
from dataclasses import dataclass

from django.conf import settings
from django.contrib.sessions.backends.base import CreateError, SessionBase

MINUTOS_LOGIN_PENDENTE = 15  # quem clicou em Conectar e não voltou do Mercado Livre
MAX_LOGIN_PENDENTE = 1000  # robôs que só abrem /entrar não enchem a memória do servidor


def _logada(dados):
    return dados.get("cliente") is not None


def _conta(dados):
    """O número da conta do Mercado Livre de uma sessão com login, ou None."""
    usuario = dados.get("usuario") if _logada(dados) else None
    return int(usuario["id"]) if usuario and usuario.get("id") is not None else None


@dataclass
class _Guardada:
    dados: dict
    ultimo_uso: float


class Sessoes:
    """Todas as sessões do servidor, pelo código que vai no cookie. Uma trava só para tudo."""

    def __init__(self, horas=None, agora=time.time, minutos_pendente=MINUTOS_LOGIN_PENDENTE,
                 max_pendentes=MAX_LOGIN_PENDENTE):
        self._horas = horas  # None: o ORZY_HORAS_SESSAO da configuração
        self._minutos_pendente = minutos_pendente
        self._max_pendentes = max_pendentes
        self.agora = agora
        self._dados = {}
        self._trava = threading.Lock()

    @property
    def horas(self):
        return settings.ORZY.horas_sessao if self._horas is None else self._horas

    def criar(self, chave, dados):
        """Guarda uma sessão nova. Devolve False se o código já existe."""
        with self._trava:
            self._limpar()
            if chave in self._dados:
                return False
            # No limite, sai a sessão sem login mais antiga. Sessões com login não contam.
            pendentes = sorted((g.ultimo_uso, c) for c, g in self._dados.items() if not _logada(g.dados))
            for _, velha in pendentes[:max(0, len(pendentes) - self._max_pendentes + 1)]:
                del self._dados[velha]
            self._dados[chave] = _Guardada(dados, self.agora())
            return True

    def guardar(self, chave, dados):
        """Atualiza uma sessão que existe. Uma que acabou (Sair em outra aba, ou o prazo) não volta."""
        with self._trava:
            guardada = self._dados.get(chave)
            if guardada is not None:
                guardada.dados = dados

    def obter(self, chave):
        """Os dados da sessão, ou None se ela não existe ou já venceu. Conta como uso."""
        with self._trava:
            self._limpar()
            guardada = self._dados.get(chave)
            if guardada is None:
                return None
            guardada.ultimo_uso = self.agora()
            return guardada.dados

    def existe(self, chave):
        with self._trava:
            self._limpar()
            return chave in self._dados

    def encerrar(self, chave):
        with self._trava:
            self._dados.pop(chave, None)

    def encerrar_da_conta(self, ml_user_id):
        """Encerra as sessões com login desta conta em todos os navegadores: a conta foi apagada ou perdeu o acesso."""
        with self._trava:
            for chave in [c for c, g in self._dados.items() if _conta(g.dados) == int(ml_user_id)]:
                del self._dados[chave]

    def limpar(self, antecedencia=0):
        """Apaga as sessões vencidas sem esperar o próximo pedido, e também as que vencem nos próximos `antecedencia`
        segundos: quem limpa a cada minuto passa 60, e nenhuma sessão fica na memória além do prazo."""
        with self._trava:
            self._limpar(antecedencia)

    def _limpar(self, antecedencia=0):
        momento = self.agora() + antecedencia
        com_login, sem_login = momento - self.horas * 3600, momento - self._minutos_pendente * 60
        for chave in [c for c, g in self._dados.items()
                      if self._comeco(g) < (com_login if _logada(g.dados) else sem_login)]:
            del self._dados[chave]

    @staticmethod
    def _comeco(guardada):
        """De onde conta o prazo: o login, para quem entrou (usar o site não estica); o último uso, para quem não
        voltou do Mercado Livre."""
        login_em = guardada.dados.get("login_em")
        if _logada(guardada.dados) and login_em is not None:
            return login_em
        return guardada.ultimo_uso


GUARDADAS = Sessoes()


def marcar_login(sessao):
    """Marca a hora do login, de onde conta o prazo da sessão."""
    sessao["login_em"] = GUARDADAS.agora()


def logada(request):
    """A sessão, se a pessoa já concluiu o login com o Mercado Livre; senão None."""
    return request.session if _logada(request.session) else None


class SessionStore(SessionBase):
    """O motor de sessão do Django em cima de GUARDADAS."""

    def load(self):
        dados = GUARDADAS.obter(self.session_key)
        if dados is None:
            self._session_key = None
            return {}
        return dados

    def exists(self, session_key):
        return GUARDADAS.existe(session_key)

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if self.session_key is None:
            return self.create()
        dados = self._get_session(no_load=must_create)
        if must_create:
            if not GUARDADAS.criar(self.session_key, dados):
                raise CreateError
        else:
            GUARDADAS.guardar(self.session_key, dados)

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        GUARDADAS.encerrar(session_key)

    @classmethod
    def clear_expired(cls):
        GUARDADAS.limpar()
