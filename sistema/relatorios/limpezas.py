"""Limpezas em segundo plano: o histórico antigo (uma vez por dia) e as sessões vencidas (a cada minuto).

Quem liga é o orzy/wsgi.py, só no servidor de verdade: os testes e o migrate não ligam.
"""

import logging
import threading

from contas.sessoes import GUARDADAS
from django.db import connections

from .historico import DIAS_DE_HISTORICO, HISTORICO

UM_DIA = 24 * 3600
UM_MINUTO = 60


def apagar_antigos_todo_dia(historico, parar, intervalo=UM_DIA):
    """Apaga os relatórios e as contagens do beta com mais de 12 meses agora e depois a cada intervalo, até `parar`.

    A Política de Privacidade promete 12 meses: com o servidor ligado por semanas, não basta apagar ao ligar.
    """
    while True:
        try:
            apagados = historico.apagar_antigos(DIAS_DE_HISTORICO)
            if apagados:
                logging.info("Histórico: %d relatório(s) com mais de %d dias foram apagados.",
                             apagados, DIAS_DE_HISTORICO)
        except Exception:
            logging.exception("Não consegui apagar o histórico antigo; tento de novo no próximo ciclo")
        finally:
            connections.close_all()  # a conexão não fica parada um dia inteiro
        if parar.wait(intervalo):
            return


def apagar_sessoes_vencidas_sempre(sessoes, parar, intervalo=UM_MINUTO):
    """Apaga as sessões vencidas a cada intervalo, até `parar`, mesmo sem ninguém usando o site.

    A Política de Privacidade promete tirar o login da memória no máximo 8 horas depois da entrada: sem isto, uma
    sessão vencida só sai no próximo pedido. Apaga um intervalo antes do prazo, para nenhuma passar dele.
    """
    while True:
        try:
            sessoes.limpar(antecedencia=intervalo)
        except Exception:
            logging.exception("Não consegui apagar as sessões vencidas; tento de novo no próximo ciclo")
        if parar.wait(intervalo):
            return


def ligar(parar, historico=HISTORICO, sessoes=GUARDADAS):
    """Liga em segundo plano a limpeza do histórico (uma vez por dia) e a das sessões (a cada minuto)."""
    for alvo, guardados, nome in ((apagar_antigos_todo_dia, historico, "limpeza-do-historico"),
                                  (apagar_sessoes_vencidas_sempre, sessoes, "limpeza-das-sessoes")):
        threading.Thread(target=alvo, args=(guardados, parar), name=nome, daemon=True).start()
