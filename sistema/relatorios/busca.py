"""Busca pelo título e filtro por situação na lista "Todos os anúncios" (resultado e histórico)."""

import unicodedata

import analise

MAX_BUSCA = 100  # letras: mais que isso não ajuda a achar um título


def ler(parametros):
    """A busca e a situação pedidas no endereço (?busca=...&situacao=...). Situação desconhecida vale como todas.

    parametros: o request.GET do Django (ou qualquer dicionário de textos).
    """
    busca = " ".join((parametros.get("busca") or "").split())[:MAX_BUSCA]
    situacao = parametros.get("situacao") or ""
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
