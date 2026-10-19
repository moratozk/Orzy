"""Limpezas em segundo plano: o histórico antigo e as contas (uma vez por dia) e as sessões vencidas (a cada minuto).

Quem liga é o orzy/wsgi.py, só no servidor de verdade: os testes e o migrate não ligam.
"""

import logging
import threading

from contas import acesso
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


def conferir_contas_todo_dia(contas, parar, intervalo=UM_DIA):
    """Agora e depois a cada intervalo, até `parar`: renova o acesso guardado de cada conta (assim ele não vence e o
    Orzy percebe quem tirou a permissão no Mercado Livre) e apaga as contas sem acesso há mais de 30 dias.

    `contas` é o módulo contas/acesso.py (os testes passam outro).
    """
    while True:
        try:
            renovadas, perdidas, falhas = contas.conferir_todos()
            if renovadas or perdidas or falhas:
                logging.info("Contas: %d acesso(s) renovado(s), %d recusado(s) pelo Mercado Livre, %d com erro.",
                             renovadas, perdidas, falhas)
            apagadas = contas.apagar_sem_acesso()
            if apagadas:
                logging.info("Contas: %d conta(s) sem acesso há mais de %d dias foram apagadas.",
                             apagadas, contas.DIAS_SEM_ACESSO)
        except Exception:
            logging.exception("Não consegui conferir as contas; tento de novo no próximo ciclo")
        finally:
            connections.close_all()
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


def ligar(parar, historico=HISTORICO, sessoes=GUARDADAS, contas=acesso):
    """Liga em segundo plano a limpeza do histórico e a conferência das contas (uma vez por dia) e a das sessões (a
    cada minuto)."""
    for alvo, guardados, nome in ((apagar_antigos_todo_dia, historico, "limpeza-do-historico"),
                                  (conferir_contas_todo_dia, contas, "conferir-as-contas"),
                                  (apagar_sessoes_vencidas_sempre, sessoes, "limpeza-das-sessoes")):
        threading.Thread(target=alvo, args=(guardados, parar), name=nome, daemon=True).start()
