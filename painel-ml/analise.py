"""
Análise dos anúncios: em que situação cada um está e o que mudar nele.

Aqui só tem regras, nada fala com o Mercado Livre: o meus_anuncios.py busca os dados e
chama estas funções, e o site da fase 3 vai usar as mesmas.

Os números abaixo são pontos de partida e podem ser ajustados. Os que vêm da
documentação do Mercado Livre estão marcados assim.
"""

import re
import unicodedata

# ---------------------------------------------------------------- situação

POUCAS_VISITAS = 30      # abaixo disso no período, o anúncio quase não está sendo encontrado
CONVERSAO_BAIXA = 0.01   # 1%: abaixo disso, vende pouco para as visitas que recebe

# Em ordem de prioridade: os primeiros são os que mais valem a pena mexer.
SITUACOES = {
    "VISITA SEM VENDA": "As pessoas veem e não compram: revise preço, fotos, frete e descrição.",
    "CONVERTE POUCO": "Vende pouco para as visitas que tem: compare preço e frete com os concorrentes.",
    "POUCA VISITA": "Quase ninguém encontra: revise título, palavras-chave, categoria e ficha técnica.",
    "VENDE, MAS POUCO VISTO": "Quem vê, compra: vale melhorar o título ou anunciar para ganhar visitas.",
    "VENDENDO BEM": "Está funcionando: use como modelo para os outros anúncios.",
    "SEM DADOS": "Não consegui ler as visitas ou as vendas deste anúncio.",
}
ORDEM = list(SITUACOES)

PROBLEMA_DE_VENDA = {"VISITA SEM VENDA", "CONVERTE POUCO"}        # é visto, mas não vende
PROBLEMA_DE_VISITA = {"POUCA VISITA", "VENDE, MAS POUCO VISTO"}  # quase não é visto


def classificar(visitas, vendas):
    if visitas is None or vendas is None:
        return "SEM DADOS"
    if visitas < POUCAS_VISITAS:
        return "VENDE, MAS POUCO VISTO" if vendas > 0 else "POUCA VISITA"
    if vendas == 0:
        return "VISITA SEM VENDA"
    if vendas / visitas < CONVERSAO_BAIXA:
        return "CONVERTE POUCO"
    return "VENDENDO BEM"


# ---------------------------------------------------------------- o que mudar

# Peso de cada sugestão: as mais pesadas aparecem primeiro, e a soma decide quais anúncios vêm antes.
ALTA, MEDIA, BAIXA = 3, 2, 1

TITULO_MAX_PADRAO = 60   # o limite mais comum; quando a categoria informa o dela, vale o da categoria
TITULO_CURTO = 0.6       # título usando menos de 60% do limite deixa palavras de busca de fora
MIN_FOTOS = 3            # do Mercado Livre: "suba pelo menos 3" fotos
LARGURA_ZOOM = 800       # do Mercado Livre: o zoom só aparece em fotos com mais de 800 px de largura
FICHA_POUCO_PREENCHIDA = 0.5  # menos da metade dos campos da ficha técnica preenchidos

# Do Mercado Livre: não pôr no título frete, parcelamento, devolução, desconto nem o estado do produto.
# Isso já aparece em outras partes do anúncio e só ocupa o espaço das palavras de busca.
FORA_DO_TITULO = [
    "frete grátis", "frete gratuito", "envio grátis", "entrega grátis", "sem juros", "parcelado",
    "devolução grátis", "promoção", "promoções", "oferta", "desconto", "liquidação", "queima de estoque",
    "black friday", "imperdível", "usado", "usada", "seminovo", "seminova", "recondicionado",
    "recondicionada", "lacrado", "lacrada",
]
# Do Mercado Livre: falar de estoque no título pode fazer o anúncio ser moderado.
ESTOQUE_NO_TITULO = ["pronta entrega", "envio imediato", "últimas unidades", "última unidade"]
# Do Mercado Livre: evitar símbolos no título. Emojis também contam.
SIMBOLOS = "!*$#@~^|=<>?"

# Campos que o vendedor não preenche na ficha técnica: o Mercado Livre esconde ou preenche sozinho,
# ou eles ficam nas variações (cor, tamanho).
TAGS_FORA_DA_FICHA = {"hidden", "read_only", "fixed", "inferred", "others", "allow_variations",
                      "variation_attribute"}
FORA_DA_FICHA = {"SELLER_SKU", "ITEM_CONDITION"}  # código interno do vendedor e o estado (novo ou usado)

# Nomes que o Mercado Livre usa no Brasil para o nível de qualidade.
NIVEIS = {"Bad": "Básica", "Average": "Satisfatória", "Good": "Profissional"}
# Regras do Mercado Livre que pedem o mesmo que uma regra do Orzy: fica só o texto do Mercado Livre.
MESMO_TEMA = {"PICTURES_QUANTITY_MIN": "fotos_quantidade", "HAS_FREE_SHIPPING": "frete"}


def _sugestao(tema, peso, texto, origem="Orzy"):
    return {"tema": tema, "peso": peso, "texto": texto, "origem": origem}


def _dicts(valor):
    """Os itens de uma lista que vieram no formato esperado. Um formato diferente não derruba o relatório."""
    return [v for v in valor if isinstance(v, dict)] if isinstance(valor, list) else []


def _primeiro_texto(*valores):
    return next((v.strip() for v in valores if isinstance(v, str) and v.strip()), "")


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


def _achar(titulo, termos):
    normal = _sem_acento(titulo)
    return [t for t in termos
            if re.search(r"(?<![a-z0-9])" + re.escape(_sem_acento(t)) + r"s?(?![a-z0-9])", normal)]


def _e(itens):
    itens = list(itens)
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


def analisar_titulo(item, max_titulo=None):
    titulo = _primeiro_texto(item.get("title"))
    if not titulo:
        return []
    limite = max_titulo if isinstance(max_titulo, int) and max_titulo > 0 else TITULO_MAX_PADRAO
    sugestoes = []

    estoque = _achar(titulo, ESTOQUE_NO_TITULO)
    if estoque:
        sugestoes.append(_sugestao("titulo_estoque", ALTA,
                                   f"Tire do título: {_e(estoque)}. Falar de estoque no título "
                                   "pode fazer o Mercado Livre moderar o anúncio."))
    if len(titulo) < limite * TITULO_CURTO:
        sugestoes.append(_sugestao("titulo_tamanho", MEDIA,
                                   f"Título curto ({len(titulo)} de {limite} caracteres): use o espaço com "
                                   "produto, marca, modelo e características principais, que são as "
                                   "palavras que as pessoas buscam."))
    fora = _achar(titulo, FORA_DO_TITULO)
    if re.search(r"\d\s*%\s*off(?![a-z0-9])", _sem_acento(titulo)):
        fora.append("% OFF")
    if fora:
        sugestoes.append(_sugestao("titulo_palavras", MEDIA,
                                   f"Tire do título: {_e(fora)}. O Mercado Livre pede para não pôr frete, "
                                   "parcelamento, desconto nem o estado do produto no título: isso já "
                                   "aparece no anúncio e só ocupa espaço."))
    simbolos = []
    for c in titulo:
        if (c in SIMBOLOS or unicodedata.category(c) == "So") and c != "°" and c not in simbolos:
            simbolos.append(c)
    if simbolos:
        sugestoes.append(_sugestao("titulo_simbolos", BAIXA,
                                   f"Tire os símbolos do título ({' '.join(simbolos)}): "
                                   "o Mercado Livre pede para não usar."))
    return sugestoes


def _largura(foto):
    tamanho = _primeiro_texto(foto.get("max_size"), foto.get("size"))
    achado = re.fullmatch(r"(\d+)\s*x\s*\d+", tamanho)
    return int(achado.group(1)) if achado else None


def analisar_fotos(item):
    fotos = item.get("pictures")
    if not isinstance(fotos, list):
        return []  # o campo não veio: não dá para julgar
    sugestoes = []
    if len(fotos) < MIN_FOTOS:
        sugestoes.append(_sugestao("fotos_quantidade", ALTA,
                                   f"Coloque pelo menos {MIN_FOTOS} fotos, mostrando o produto de ângulos "
                                   f"diferentes (tem {len(fotos)})."))
    larguras = [_largura(f) for f in _dicts(fotos)]
    pequenas = sum(1 for l in larguras if l is not None and l <= LARGURA_ZOOM)
    if pequenas:
        if len(fotos) == 1:
            quais = f"A foto tem até {LARGURA_ZOOM} px de largura e fica"
        elif pequenas == len(fotos):
            quais = f"As {pequenas} fotos têm até {LARGURA_ZOOM} px de largura e ficam"
        elif pequenas == 1:
            quais = f"1 de {len(fotos)} fotos tem até {LARGURA_ZOOM} px de largura e fica"
        else:
            quais = f"{pequenas} de {len(fotos)} fotos têm até {LARGURA_ZOOM} px de largura e ficam"
        sugestoes.append(_sugestao("fotos_tamanho", BAIXA,
                                   f"{quais} sem zoom: o Mercado Livre recomenda fotos de 1200 x 1200 px."))
    return sugestoes


def _tags(atributo):
    tags = atributo.get("tags") or {}
    if isinstance(tags, dict):
        return {k for k, v in tags.items() if v}
    return set(tags)


def _entra_na_ficha(atributo):
    return atributo.get("id") not in FORA_DA_FICHA and not (_tags(atributo) & TAGS_FORA_DA_FICHA)


def _obrigatorio(atributo, condicao):
    tags = _tags(atributo)
    return "required" in tags or ("new_required" in tags and condicao == "new")


def _respondido(atributo):
    if str(atributo.get("value_id")) == "-1":
        return True  # marcado como "não se aplica"
    if atributo.get("value_name"):
        return True
    return any(v.get("name") for v in _dicts(atributo.get("values")))


def analisar_ficha(item, atributos_categoria):
    """Compara a ficha técnica do anúncio com os campos que a categoria tem."""
    marcado = "incomplete_technical_specs" in (item.get("tags") or [])
    aviso_ml = "O Mercado Livre marcou a ficha técnica deste anúncio como incompleta, e isso diminui a exposição."
    campos = [a for a in _dicts(atributos_categoria) if _entra_na_ficha(a)]
    respondidos = {a.get("id") for a in _dicts(item.get("attributes")) if _respondido(a)}
    faltam = [a for a in campos if a.get("id") not in respondidos]
    if not faltam:
        return [_sugestao("ficha", ALTA, aviso_ml + " Complete os campos que faltam.")] if marcado else []

    condicao = item.get("condition")

    def relevancia(a):
        r = a.get("relevance")
        return r if isinstance(r, (int, float)) else 9

    faltam.sort(key=lambda a: (not _obrigatorio(a, condicao), relevancia(a)))
    nomes = [_primeiro_texto(a.get("name"), a.get("id"), "?")
             + (" (obrigatório)" if _obrigatorio(a, condicao) else "") for a in faltam]
    preenchidos = len(campos) - len(faltam)
    if marcado or any(_obrigatorio(a, condicao) for a in faltam):
        peso = ALTA
    elif preenchidos < len(campos) * FICHA_POUCO_PREENCHIDA:
        peso = MEDIA
    else:
        peso = BAIXA
    mais = f" e mais {len(nomes) - 5}" if len(nomes) > 5 else ""
    texto = (f"Complete a ficha técnica ({preenchidos} de {len(campos)} campos preenchidos). "
             f"Faltam: {', '.join(nomes[:5])}{mais}. Com a ficha completa, o anúncio aparece "
             "nos filtros da busca.")
    if marcado:
        texto += " " + aviso_ml
    return [_sugestao("ficha", peso, texto)]


def analisar_frete(item, situacao):
    envio = item.get("shipping")
    if not isinstance(envio, dict) or envio.get("free_shipping") is not False:
        return []
    if situacao not in PROBLEMA_DE_VENDA | PROBLEMA_DE_VISITA:
        return []  # custa dinheiro: só vale sugerir quando o anúncio tem problema de visita ou de venda
    return [_sugestao("frete", MEDIA, "Ofereça frete grátis, se a margem permitir: o anúncio fica mais "
                                      "competitivo, mas o envio passa a ser pago por você.")]


def analisar_tipo(item, situacao):
    tipo = item.get("listing_type_id")
    if tipo == "free" and situacao in PROBLEMA_DE_VENDA | PROBLEMA_DE_VISITA:
        return [_sugestao("tipo", ALTA, "Mude o anúncio de Grátis para Clássico: o Grátis aparece pouco "
                                        "nas buscas. O Clássico cobra uma tarifa por venda.")]
    if tipo == "gold_special" and situacao in PROBLEMA_DE_VENDA:
        return [_sugestao("tipo", BAIXA, "Teste o Premium: ele oferece parcelamento sem juros, o que ajuda "
                                         "quem visita a decidir. A tarifa por venda é maior que a do Clássico.")]
    return []


def ler_qualidade(resposta):
    """Resume a resposta de /item/{id}/performance: nota de 0 a 100, nível e o que o Mercado Livre pede.

    Resposta vazia quer dizer que o Mercado Livre ainda não calculou a nota do anúncio.
    """
    resposta = resposta if isinstance(resposta, dict) else {}
    pedidos = []
    vistos = set()
    for grupo in _dicts(resposta.get("buckets")):
        for variavel in _dicts(grupo.get("variables")):
            regras = [r for r in _dicts(variavel.get("rules")) if r.get("status") == "PENDING"]
            if not regras and variavel.get("status") == "PENDING":
                regras = [{"key": variavel.get("key")}]
            for regra in regras:
                textos = regra.get("wordings") if isinstance(regra.get("wordings"), dict) else {}
                texto = _primeiro_texto(textos.get("title"), variavel.get("title"), textos.get("label")).rstrip(".")
                if not texto or texto in vistos:
                    continue
                vistos.add(texto)
                tema = MESMO_TEMA.get(regra.get("key"), f"ml:{regra.get('key')}")
                peso = ALTA if regra.get("mode") == "WARNING" else MEDIA
                pedidos.append(_sugestao(tema, peso, f"{texto} (pedido do ML).", origem="ML"))
    nota = resposta.get("score")
    return {
        "nota": nota if isinstance(nota, (int, float)) and not isinstance(nota, bool) else None,
        "nivel": _primeiro_texto(resposta.get("level_wording")) or NIVEIS.get(resposta.get("level")),
        "pedidos": pedidos,
    }


def texto_qualidade(qualidade):
    """Como a nota aparece no relatório: "Satisfatória (69/100)", "ainda sem nota" ou "?" se não deu para ler."""
    if qualidade is None:
        return "?"
    nota, nivel = qualidade.get("nota"), qualidade.get("nivel")
    if nota is None:
        return nivel or "ainda sem nota"
    numero = f"{round(nota)}/100"
    return f"{nivel} ({numero})" if nivel else numero


def sugerir(item, situacao, categoria=None, qualidade=None):
    """Lista do que mudar no anúncio, da sugestão mais importante para a menos.

    item: o anúncio como o Mercado Livre devolve (title, pictures, attributes, shipping, listing_type_id...).
    situacao: uma das SITUACOES.
    categoria: {"max_titulo": ..., "atributos": [...]} da categoria do anúncio, ou None.
    qualidade: o que ler_qualidade() devolveu, ou None.
    Cada sugestão é um dicionário com tema, peso, texto e origem ("Orzy" ou "ML").
    """
    categoria = categoria or {}
    nossas = (analisar_titulo(item, categoria.get("max_titulo"))
              + analisar_fotos(item)
              + analisar_ficha(item, categoria.get("atributos"))
              + analisar_frete(item, situacao)
              + analisar_tipo(item, situacao))
    peso_nosso = {}
    for s in nossas:
        peso_nosso[s["tema"]] = max(peso_nosso.get(s["tema"], 0), s["peso"])
    # Quando o Mercado Livre pede o mesmo que uma regra nossa, fica o texto dele, com o peso maior dos dois.
    do_ml = [dict(p, peso=max(p["peso"], peso_nosso.get(p["tema"], 0)))
             for p in (qualidade or {}).get("pedidos") or []]
    temas_do_ml = {p["tema"] for p in do_ml}
    todas = do_ml + [s for s in nossas if s["tema"] not in temas_do_ml]
    return sorted(todas, key=lambda s: -s["peso"])


def pontos(sugestoes):
    """Quanto o anúncio precisa de mudança: a soma dos pesos das sugestões."""
    return sum(s["peso"] for s in sugestoes)
