"""Relatórios gerados em segundo plano. A página pergunta o andamento enquanto o relatório roda.

O resultado fica na memória da sessão (para ver e baixar o CSV) e no histórico. Cada relatório que termina entra nas
contagens do beta (ver contagens.py): só se deu certo ou não e quantos anúncios leu, sem dizer de quem.
"""

import logging
import secrets
import threading

import meus_anuncios
import ml_api
from django.conf import settings
from django.db import connections

from . import contagens, datas
from .historico import HISTORICO

GERANDO = "gerando"
PRONTO = "pronto"
ERRO = "erro"

MENSAGEM_INESPERADA = "Algo inesperado aconteceu ao gerar o relatório. Tente de novo em alguns minutos."
OPCOES_DIAS = (30, 60, 90, 150)

# As etapas de meus_anuncios.coletar, na ordem, com o peso de cada uma no anel de andamento: visitas e nota fazem uma
# consulta por anúncio e levam quase todo o tempo. Se coletar() ganhar uma etapa, ela entra aqui também (um teste
# confere).
PASSOS = (("Anúncios ativos", 1), ("Detalhes dos anúncios", 1), ("Ficha técnica", 1), ("Visitas", 4),
          ("Vendas", 1), ("Nota do Mercado Livre", 4))


class ErroRelatorio(Exception):
    """Não dá para gerar agora (outro relatório em andamento, por exemplo). A mensagem vai para a página."""


class Relatorio:
    def __init__(self, ml_user_id, dias):
        self.id = secrets.token_urlsafe(8)
        self.ml_user_id = ml_user_id
        self.dias = dias
        self.estado = GERANDO
        self.etapa = "Preparando o relatório..."
        self.passo = 0  # quantas etapas de PASSOS já começaram
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
            self.passo = min(self.passo + 1, len(PASSOS))

    def progredir(self, feitos, total):
        self.feitos, self.total = feitos, total

    def terminar(self, linhas, mensagem=""):
        with self._trava:
            self.linhas = linhas
            self.mensagem = mensagem
            self.gerado_em = datas.agora()
            self.estado = PRONTO

    def falhar(self, mensagem):
        with self._trava:
            self.mensagem = mensagem
            self.estado = ERRO

    def pct(self):
        """Quanto do relatório já foi feito, de 0 a 100, pelo peso das etapas. Uma estimativa: não é tempo."""
        if self.estado != GERANDO:
            return 100
        pesos = [peso for _, peso in PASSOS]
        feito = sum(pesos[:max(self.passo - 1, 0)])
        if self.passo and self.total:
            feito += pesos[self.passo - 1] * min(self.feitos / self.total, 1)
        return min(99, int(100 * feito / sum(pesos)))

    def etapas(self):
        """As etapas para a página: nome, estado ("feita", "ativa" ou ""), o que mostrar ao lado e, na que está
        andando, quanto dela já foi (barra, de 0 a 100)."""
        lista = []
        for i, (nome, _) in enumerate(PASSOS, 1):
            if i < self.passo:
                lista.append({"nome": nome, "estado": "feita", "conta": "pronto"})
            elif i == self.passo:
                conta = f"{self.feitos} de {self.total}" if self.total else "agora"
                lista.append({"nome": nome, "estado": "ativa", "conta": conta,
                              "barra": min(round(100 * self.feitos / self.total), 100) if self.total else 0})
            else:
                lista.append({"nome": nome, "estado": "", "conta": "na fila"})
        return lista

    def para_json(self):
        return {"estado": self.estado, "etapa": self.etapa, "feitos": self.feitos, "total": self.total,
                "mensagem": self.mensagem, "pct": self.pct(), "passo": self.passo, "etapas": self.etapas()}


class Relatorios:
    def __init__(self, historico, max_anuncios=None, simultaneos=2):
        self._historico = historico
        self._max = max_anuncios  # None: o ORZY_MAX_ANUNCIOS da configuração
        self._simultaneos = simultaneos  # relatórios rodando ao mesmo tempo no servidor inteiro
        self._rodando = 0
        self._trava = threading.Lock()

    @property
    def max_anuncios(self):
        return settings.ORZY.max_anuncios if self._max is None else self._max

    def iniciar(self, sessao, dias):
        """Começa um relatório da conta da sessão (já com login). Ele fica em sessao["relatorios"]."""
        with self._trava:
            if any(r.estado == GERANDO for r in sessao["relatorios"].values()):
                raise ErroRelatorio("Já tem um relatório sendo gerado. Espere ele terminar.")
            if self._rodando >= self._simultaneos:
                raise ErroRelatorio("Há muitos relatórios sendo gerados agora. Tente de novo em alguns minutos.")
            self._rodando += 1
            relatorio = Relatorio(sessao["usuario"]["id"], dias)
            sessao["relatorios"][relatorio.id] = relatorio
        relatorio.thread = threading.Thread(target=self._executar, args=(relatorio, sessao["cliente"]),
                                            name="relatorio", daemon=True)
        relatorio.thread.start()
        return relatorio

    def _executar(self, relatorio, cliente):
        contar = {}
        maximo = self.max_anuncios
        try:
            dados = meus_anuncios.coletar(cliente, relatorio.ml_user_id, relatorio.dias, limite=maximo,
                                          etapa=relatorio.andar, progresso=relatorio.progredir)
            if not dados["ids"]:
                relatorio.terminar([], "Nenhum anúncio ativo nessa conta.")
                contar = {"relatorios_prontos": 1}
                return
            linhas = meus_anuncios.montar_linhas(**dados)
            if len(dados["ids"]) >= maximo:
                relatorio.aviso = (f"Esta versão lê até {maximo} anúncios por relatório. "
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
            connections.close_all()  # a conexão com o banco desta thread não fica aberta depois dela


RELATORIOS = Relatorios(HISTORICO)


def em_andamento(sessao):
    return next((r for r in sessao["relatorios"].values() if r.estado == GERANDO), None)


def dias_pedidos(valor):
    """O período pedido no formulário. Qualquer coisa fora das opções vale como a primeira."""
    try:
        dias = int(valor)
    except (TypeError, ValueError):
        return OPCOES_DIAS[0]
    return dias if dias in OPCOES_DIAS else OPCOES_DIAS[0]
