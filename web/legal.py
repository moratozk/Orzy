"""Política de Privacidade e Termos de Uso: o site mostra os textos de docs/legal/, escritos em Markdown.

Os textos são de outra frente do projeto e mudam sem mexer no código: o site lê o arquivo a cada pedido.
Eles vêm do repositório, não de usuário, mas passam por escape do mesmo jeito. Este arquivo entende só o
pedaço de Markdown que esses textos usam: títulos, parágrafos, listas, citações, tabelas, negrito, código e links.
"""

import re
from html import escape
from pathlib import Path

PASTA_LEGAL = Path(__file__).resolve().parent.parent / "docs" / "legal"
TEXTOS = {"privacidade": "politica-de-privacidade.md", "termos": "termos-de-uso.md"}
NOMES = {"privacidade": "Política de Privacidade", "termos": "Termos de Uso"}
# Um texto que cita o outro aponta para a rota do site. Outros links relativos (como o LEIA-ME) viram só texto.
ROTAS = {arquivo: "/" + rota for rota, arquivo in TEXTOS.items()}

_TITULO = re.compile(r"(#{1,6})\s+(.*)")
_ITEM = re.compile(r"(?:[-*]|(\d+)\.)\s+(.*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_NEGRITO = re.compile(r"\*\*(.+?)\*\*")


def carregar(rota, pasta=PASTA_LEGAL):
    """HTML do texto da rota ("privacidade" ou "termos"), ou None se o arquivo ainda não existe."""
    try:
        texto = (Path(pasta) / TEXTOS[rota]).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    return para_html(texto)


def _link(achado):
    texto, destino = achado.group(1), achado.group(2)  # os dois já passaram por escape
    if destino.startswith(("https://", "http://")):
        return f'<a href="{destino}" target="_blank" rel="noopener noreferrer">{texto}</a>'
    if destino.startswith("mailto:"):  # abre o e-mail sem deixar uma aba vazia para trás
        return f'<a href="{destino}">{texto}</a>'
    arquivo, _, ancora = destino.partition("#")
    rota = ROTAS.get(arquivo)
    if rota is None:
        return texto
    return f'<a href="{rota}{"#" + ancora if ancora else ""}">{texto}</a>'


def _inline(texto):
    # O que está entre crases fica como está; no resto, links e negrito.
    partes = re.split(r"`([^`]*)`", escape(texto))
    for i, parte in enumerate(partes):
        partes[i] = f"<code>{parte}</code>" if i % 2 else _NEGRITO.sub(r"<strong>\1</strong>", _LINK.sub(_link, parte))
    return "".join(partes)


def _celulas(linha):
    return [celula.strip() for celula in linha.strip().strip("|").split("|")]


def _tabela(linhas):
    cabecalho = "".join(f"<th>{_inline(c)}</th>" for c in _celulas(linhas[0]))
    corpo = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in _celulas(linha)) + "</tr>"
                    for linha in linhas[1:] if not set(linha) <= set("|-: "))
    return f'<div class="tabela"><table><thead><tr>{cabecalho}</tr></thead><tbody>{corpo}</tbody></table></div>'


def para_html(texto):
    blocos, paragrafo, citacao, tabela, itens = [], [], [], [], []
    lista = None  # "ul" ou "ol"

    def fechar():
        nonlocal lista
        if paragrafo:
            blocos.append(f"<p>{_inline(' '.join(paragrafo))}</p>")
        if citacao:
            blocos.append(f"<blockquote><p>{_inline(' '.join(citacao))}</p></blockquote>")
        if tabela:
            blocos.append(_tabela(tabela))
        if itens:
            lis = "".join(f"<li>{_inline(' '.join(item))}</li>" for item in itens)
            blocos.append(f"<{lista}>{lis}</{lista}>")
        for aberto in (paragrafo, citacao, tabela, itens):
            aberto.clear()
        lista = None

    for linha in texto.splitlines():
        linha = linha.rstrip()
        titulo, item = _TITULO.fullmatch(linha), _ITEM.fullmatch(linha)
        if not linha.strip():
            fechar()
        elif titulo:
            fechar()
            nivel = len(titulo.group(1))
            blocos.append(f"<h{nivel}>{_inline(titulo.group(2))}</h{nivel}>")
        elif linha.startswith(">"):
            if not citacao:
                fechar()
            citacao.append(linha[1:].strip())
        elif linha.startswith("|"):
            if not tabela:
                fechar()
            tabela.append(linha)
        elif item:
            tipo = "ol" if item.group(1) else "ul"
            if not itens or tipo != lista:
                fechar()
                lista = tipo
            itens.append([item.group(2)])
        elif itens and linha.startswith(" "):
            itens[-1].append(linha.strip())  # continuação do item de cima
        else:
            if citacao or tabela or itens:
                fechar()
            paragrafo.append(linha.strip())
    fechar()
    return "\n".join(blocos)
