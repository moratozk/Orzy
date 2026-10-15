"""Contagens do beta: quantos logins e relatórios o site teve por dia, e quantas contas e anúncios o histórico tem.

Só números. As contagens por dia não dizem de quem são (nada de conta, apelido ou anúncio). As contas e os anúncios
por conta saem do histórico que já existe, na hora em que a página /contagens abre: nada novo do vendedor é guardado.
A página só abre para as contas de ORZY_CONTAS_ADMIN (ver web/LEIA-ME.md).
"""

import logging
from datetime import datetime, timezone

from .paginas import BRASILIA

# O que se conta por dia, com o nome que aparece na página, na ordem da página.
NOMES = {
    "logins": "Logins",
    "relatorios_prontos": "Relatórios sem erro",
    "erros_mercado_livre": "Erro do Mercado Livre",  # o Mercado Livre recusou ou não respondeu, ou o login venceu
    "erros_inesperados": "Erro inesperado",  # o detalhe fica no registro do servidor
    "anuncios_lidos": "Anúncios lidos",
}
DIAS_NA_PAGINA = 30


def hoje(agora=None):
    """O dia de agora no horário de Brasília ("2026-10-15"), o mesmo do calendário de quem lê a página."""
    return (agora or datetime.now(timezone.utc)).astimezone(BRASILIA).date().isoformat()


def contar(historico, **valores):
    """Soma às contagens de hoje. Uma falha aqui fica só no registro do servidor: não atrapalha login nem relatório."""
    if not valores:
        return
    try:
        historico.somar_contagens(hoje(), valores)
    except Exception:
        logging.exception("Não consegui guardar uma contagem do beta")


def resumo(historico, max_anuncios):
    """O que a página /contagens mostra: os totais, os dias mais recentes e as contas do histórico."""
    dias = historico.ler_contagens()
    por_conta = historico.ultimo_total_de_cada_conta()  # do menor para o maior
    return {
        "colunas": list(NOMES.items()),
        "desde": min(dias, default=None),
        "totais": {nome: sum(d.get(nome, 0) for d in dias.values()) for nome in NOMES},
        "dias": [(dia, {nome: dias[dia].get(nome, 0) for nome in NOMES})
                 for dia in sorted(dias, reverse=True)[:DIAS_NA_PAGINA]],
        "contas": len(por_conta),
        "anuncios": {"menor": por_conta[0], "media": round(sum(por_conta) / len(por_conta)), "maior": por_conta[-1],
                     "no_limite": sum(1 for total in por_conta if total >= max_anuncios)} if por_conta else None,
        "max_anuncios": max_anuncios,
    }
