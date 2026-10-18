"""Busca pelo título e filtro por situação na tabela "Todos os anúncios" (resultado e histórico)."""

import unicodedata
from urllib.parse import parse_qs

import analise

MAX_BUSCA = 100  # letras: mais que isso não ajuda a achar um título


def ler(consulta):
    """A busca e a situação pedidas no endereço (?busca=...&situacao=...). Situação desconhecida vale como todas."""
    parametros = parse_qs(consulta or "")
    busca = " ".join(parametros.get("busca", [""])[0].split())[:MAX_BUSCA]
    situacao = parametros.get("situacao", [""])[0]
    return busca, (situacao if situacao in analise.ORDEM else "")


def _normal(texto):
    """Sem acento e sem diferença entre maiúscula e minúscula: "camera" acha "Câmera"."""
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).casefold()


def filtrar(anuncios, busca, situacao):
    """Os anúncios na situação pedida que têm no título todas as palavras da busca, em qualquer ordem."""
    palavras = _normal(busca).split()
    achados = []
    for a in anuncios:
        titulo = _normal(a["titulo"] or "")  # uma vez por anúncio, não uma vez por palavra
        if (not situacao or a["situacao"] == situacao) and all(p in titulo for p in palavras):
            achados.append(a)
    return achados
