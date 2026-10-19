"""O que toda página pode usar no HTML."""

import re

from contas.sessoes import logada
from django.utils.functional import SimpleLazyObject
from relatorios.historico import MESES_DE_HISTORICO

CONTATO = "orzy.suporte@gmail.com"  # o mesmo da Política de Privacidade e dos Termos de Uso


def _iniciais(apelido):
    """"MARINA_SILVA" vira "MS"; uma palavra só, as duas primeiras letras."""
    partes = [p for p in re.split(r"[\W_]+", apelido) if p]
    if len(partes) > 1:
        return (partes[0][0] + partes[1][0]).upper()
    return partes[0][:2].upper() if partes else ""


def _conta(request):
    sessao = logada(request)
    apelido = (sessao["usuario"].get("apelido") or "") if sessao is not None else ""
    return {"apelido": apelido, "iniciais": _iniciais(apelido)}


def orzy(request):
    # A conta só é lida quando a página usa (o topo do sistema): as páginas públicas não abrem a sessão por causa dela.
    return {
        "contato": CONTATO,
        "meses_de_historico": MESES_DE_HISTORICO,
        "conta": SimpleLazyObject(lambda: _conta(request)),
        "caminho": request.path,
        "aba": next((aba for aba in ("relatorio", "historico") if request.path.startswith("/" + aba)), ""),
    }
