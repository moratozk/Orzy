"""Política de Privacidade e Termos de Uso: o site mostra os textos de docs/legal/, escritos em Markdown.

Os textos são de outra frente do projeto e mudam sem mexer no código: o site lê o arquivo a cada pedido. Eles vêm do
repositório, não de usuário, mas passam por escape do mesmo jeito. Este arquivo entende só o pedaço de Markdown que
esses textos usam: títulos, parágrafos, listas, citações, tabelas, negrito, código e links.

Para a página do visual novo, faz o mesmo que orzy/marca/visual-novo/fonte/legal_md.py faz no pacote do visual:
- cada título ## e ### ganha um id (para o índice e para links como /privacidade#8-os-seus-direitos) e o número do
  começo ("1.", "2.1") vira um selo;
- o que vem antes do primeiro ## vai para a cabeça da página: título, aviso de rascunho, versão e abertura;
- cada célula de tabela leva o nome da coluna em data-label (no celular, a tabela vira cartões sem script);
- [PREENCHER: ...] e [CONFIRMAR: ...] viram uma marca visível (só existem no rascunho; somem antes de publicar).
"""

import re
import unicodedata
from html import escape
from pathlib import Path

from django.conf import settings

TEXTOS = {"privacidade": "politica-de-privacidade.md", "termos": "termos-de-uso.md"}
NOMES = {"privacidade": "Política de Privacidade", "termos": "Termos de Uso"}
# Um texto que cita o outro aponta para a rota do site. Outros links relativos (como o LEIA-ME) viram só texto.
ROTAS = {arquivo: "/" + rota for rota, arquivo in TEXTOS.items()}
PALAVRAS_POR_MINUTO = 200

_TITULO = re.compile(r"(#{1,6})\s+(.*)")
_ITEM = re.compile(r"(?:[-*]|(\d+)\.)\s+(.*)")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_NEGRITO = re.compile(r"\*\*(.+?)\*\*")
_PENDENTE = re.compile(r"\[(PREENCHER|CONFIRMAR):?\s*([^\]]+)\]")
_NUMERO = re.compile(r"(\d+(?:\.\d+)*)\.?\s+(.*)")
_VERSAO = re.compile(r"\*\*Versão:\*\*\s*(.*)")


def carregar(rota, pasta=None):
    """O texto da rota ("privacidade" ou "termos") em partes da página (ver documento), ou None se o arquivo ainda
    não existe. pasta: onde estão os textos (o padrão é o ORZY_PASTA_LEGAL da configuração, docs/legal/)."""
    try:
        texto = (Path(pasta or settings.ORZY_PASTA_LEGAL) / TEXTOS[rota]).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    return documento(texto)


def _slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


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


def _pendente(achado):
    tipo = achado.group(1).capitalize()
    return f'<mark class="lg-pendente lg-{tipo.lower()}"><b>{tipo}</b> {achado.group(2)}</mark>'


def _inline(texto):
    # O que está entre crases fica como está; no resto, links, negrito e as marcas do rascunho.
    partes = re.split(r"`([^`]*)`", escape(texto))
    for i, parte in enumerate(partes):
        if i % 2:
            partes[i] = f"<code>{parte}</code>"
        else:
            parte = _NEGRITO.sub(r"<strong>\1</strong>", _LINK.sub(_link, parte))
            partes[i] = _PENDENTE.sub(_pendente, parte)
    return "".join(partes)


def _sem_tags(html):
    return re.sub(r"<[^>]+>", "", html)


def _celulas(linha):
    return [celula.strip() for celula in linha.strip().strip("|").split("|")]


def _tabela(linhas):
    cabecalho = [_inline(c) for c in _celulas(linhas[0])]
    rotulos = [escape(_sem_tags(c), quote=True) for c in cabecalho]
    # Os papéis (role) seguram a leitura de tabela quando o CSS do celular transforma as linhas em cartões.
    th = "".join(f'<th scope="col" role="columnheader">{c}</th>' for c in cabecalho)
    corpo = ""
    for linha in linhas[1:]:
        if set(linha) <= set("|-: "):
            continue
        tds = "".join(f'<td role="cell" data-label="{rotulos[i] if i < len(rotulos) else ""}">{_inline(c)}</td>'
                      for i, c in enumerate(_celulas(linha)))
        corpo += f'<tr role="row">{tds}</tr>'
    return (f'<div class="tabela"><table role="table"><thead role="rowgroup"><tr role="row">{th}</tr></thead>'
            f'<tbody role="rowgroup">{corpo}</tbody></table></div>')


def blocos(texto):
    """Lista de (tipo, html, extra): tipo é titulo1, titulo (com extra = (nivel, id, numero, texto)), citacao,
    paragrafo (com extra = o texto cru), lista ou tabela. Lê linha a linha."""
    saida, paragrafo, citacao, tabela, itens = [], [], [], [], []
    lista = None  # "ul" ou "ol"
    ids = set()

    def fechar():
        nonlocal lista
        if paragrafo:
            bruto = " ".join(paragrafo)
            saida.append(("paragrafo", f"<p>{_inline(bruto)}</p>", bruto))
        if citacao:
            saida.append(("citacao", f"<blockquote><p>{_inline(' '.join(citacao))}</p></blockquote>", None))
        if tabela:
            saida.append(("tabela", _tabela(tabela), None))
        if itens:
            lis = "".join(f"<li>{_inline(' '.join(item))}</li>" for item in itens)
            saida.append(("lista", f"<{lista}>{lis}</{lista}>", None))
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
            nivel, bruto = len(titulo.group(1)), titulo.group(2).strip()
            if nivel == 1:
                saida.append(("titulo1", _inline(bruto), bruto))
                continue
            numero = _NUMERO.fullmatch(bruto)
            num, resto = (numero.group(1), numero.group(2)) if numero else ("", bruto)
            ident = base = _slug(bruto)
            k = 2
            while ident in ids:  # dois títulos iguais não ficam com o mesmo id
                ident, k = f"{base}-{k}", k + 1
            ids.add(ident)
            marca = f'<span class="lg-num">{num}</span> ' if num else ""
            saida.append(("titulo", f'<h{nivel} id="{ident}">{marca}{_inline(resto)}</h{nivel}>',
                          (nivel, ident, num, resto)))
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
    return saida


def documento(texto):
    """O texto em partes da página: titulo, aviso, versao, lide (o que vem antes do primeiro ##), corpo (do primeiro
    ## em diante), indice [{id, numero, texto}] dos ## e minutos de leitura. Tudo em HTML, já com escape."""
    titulo, aviso, versao, lide, corpo, indice = "", "", "", [], [], []
    antes = True
    for tipo, html, extra in blocos(texto):
        if tipo == "titulo" and extra[0] == 2:
            antes = False
            indice.append({"id": extra[1], "numero": extra[2], "texto": _inline(extra[3])})
        if antes:
            if tipo == "titulo1":
                titulo = html
            elif tipo == "citacao" and not aviso:
                aviso = html
            elif tipo == "paragrafo" and _VERSAO.fullmatch(extra) and not versao:
                versao = _inline(_VERSAO.fullmatch(extra).group(1))
            else:
                lide.append(html)
        else:
            corpo.append(html)
    # A leitura conta o que a pessoa lê: sem o aviso de rascunho e sem os endereços dos links.
    sem_aviso = "\n".join(linha for linha in texto.splitlines() if not linha.startswith(">"))
    palavras = len(re.findall(r"\w+", re.sub(r"\]\([^)]*\)", "]", sem_aviso)))
    return {"titulo": titulo, "aviso": aviso, "versao": versao, "lide": "\n".join(lide), "corpo": "\n".join(corpo),
            "indice": indice, "minutos": max(1, round(palavras / PALAVRAS_POR_MINUTO))}
