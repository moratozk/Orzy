"""Relatórios gerados em segundo plano. A página pergunta o andamento enquanto o relatório roda.

O resultado fica na memória da sessão (para ver e baixar o CSV) e no histórico. Cada relatório que termina entra nas
contagens do beta (ver contagens.py): só se deu certo ou não e quantos anúncios leu, sem dizer de quem.
"""

import logging
import secrets
import threading
from datetime import datetime, timezone

import meus_anuncios
import ml_api

from . import contagens

GERANDO = "gerando"
PRONTO = "pronto"
ERRO = "erro"

MENSAGEM_INESPERADA = "Algo inesperado aconteceu ao gerar o relatório. Tente de novo em alguns minutos."


class ErroRelatorio(Exception):
    """Não dá para gerar agora (outro relatório em andamento, por exemplo). A mensagem vai para a página."""


class Relatorio:
    def __init__(self, ml_user_id, dias):
        self.id = secrets.token_urlsafe(8)
        self.ml_user_id = ml_user_id
        self.dias = dias
        self.estado = GERANDO
        self.etapa = "Preparando o relatório..."
        self.feitos = 0
        self.total = 0
        self.linhas = []
        self.aviso = ""  # ex.: "lê até 300 anúncios por relatório"
        self.mensagem = ""  # o que aconteceu, quando deu erro ou não há anúncios
        self.gerado_em = None  # quando os dados terminaram de chegar do Mercado Livre (UTC)
        self.historico_id = None  # número dele no histórico, depois de guardado
        self.thread = None
        self._trava = threading.Lock()

    def andar(self, etapa):
        with self._trava:
            self.etapa, self.feitos, self.total = etapa, 0, 0

    def progredir(self, feitos, total):
        self.feitos, self.total = feitos, total

    def terminar(self, linhas, mensagem=""):
        with self._trava:
            self.linhas = linhas
            self.mensagem = mensagem
            self.gerado_em = datetime.now(timezone.utc)
            self.estado = PRONTO

    def falhar(self, mensagem):
        with self._trava:
            self.mensagem = mensagem
            self.estado = ERRO

    def para_json(self):
        return {"estado": self.estado, "etapa": self.etapa, "feitos": self.feitos,
                "total": self.total, "mensagem": self.mensagem}


class Relatorios:
    def __init__(self, historico, max_anuncios, simultaneos=2):
        self._historico = historico
        self._max = max_anuncios
        self._simultaneos = simultaneos  # relatórios rodando ao mesmo tempo no servidor inteiro
        self._rodando = 0
        self._trava = threading.Lock()

    def iniciar(self, sessao, cliente, dias):
        with self._trava:
            if any(r.estado == GERANDO for r in sessao.relatorios.values()):
                raise ErroRelatorio("Já tem um relatório sendo gerado. Espere ele terminar.")
            if self._rodando >= self._simultaneos:
                raise ErroRelatorio("Há muitos relatórios sendo gerados agora. Tente de novo em alguns minutos.")
            self._rodando += 1
            relatorio = Relatorio(sessao.usuario["id"], dias)
            sessao.relatorios[relatorio.id] = relatorio
        relatorio.thread = threading.Thread(target=self._executar, args=(relatorio, cliente), daemon=True)
        relatorio.thread.start()
        return relatorio

    def _executar(self, relatorio, cliente):
        contar = {}
        try:
            dados = meus_anuncios.coletar(cliente, relatorio.ml_user_id, relatorio.dias, limite=self._max,
                                          etapa=relatorio.andar, progresso=relatorio.progredir)
            if not dados["ids"]:
                relatorio.terminar([], "Nenhum anúncio ativo nessa conta.")
                contar = {"relatorios_prontos": 1}
                return
            linhas = meus_anuncios.montar_linhas(**dados)
            if len(dados["ids"]) >= self._max:
                relatorio.aviso = (f"Esta versão lê até {self._max} anúncios por relatório. "
                                   "Se você tem mais, os que sobraram não entram aqui.")
            try:
                relatorio.historico_id = self._historico.salvar(relatorio.ml_user_id, relatorio.dias, linhas)
            except Exception:
                logging.exception("Não consegui salvar o histórico de um relatório")
            relatorio.terminar(linhas)
            contar = {"relatorios_prontos": 1, "anuncios_lidos": len(linhas)}
        except ml_api.ErroML as e:
            relatorio.falhar(str(e))
            contar = {"erros_mercado_livre": 1}
        except Exception:
            logging.exception("Falha ao gerar um relatório")
            relatorio.falhar(MENSAGEM_INESPERADA)
            contar = {"erros_inesperados": 1}
        finally:
            with self._trava:
                self._rodando -= 1
            contagens.contar(self._historico, **contar)  # depois de o resultado aparecer: não atrasa a página
