"""O que cada tela do relatório e do histórico mostra, já calculado: os modelos (templates) só arrumam na página.

Os textos que vêm do Mercado Livre (títulos, notas) vão como estão: o modelo do Django faz o escape.
"""

import analise

from . import busca as filtro
from . import datas, formatos
from .geracao import OPCOES_DIAS, PASSOS, PRONTO

MAX_PRIORIDADES = 10
SUGESTOES_POR_ANUNCIO = 3
# O ícone de cada situação com problema na lista "O que olhar primeiro" (os do sprite do visual novo).
ICONES_PENDENCIA = {"vsv": "i-olho", "cp": "i-alvo", "pv": "i-busca", "vpv": "i-sacola"}


def _plural(n, um, varios):
    return f"{formatos.milhar(n)} {um if n == 1 else varios}"


def _link(linha):
    url = linha.get("link") or ""
    return url if url.startswith("https://") else ""


def _sugestao(s):
    return {"area": formatos.area(s["tema"]), "texto": s["texto"], "peso": s["peso"],
            "prioridade": formatos.NOMES_PRIORIDADE.get(s["peso"], "")}


def _cartao(linha):
    """Um anúncio de "Comece por estes": as primeiras sugestões e o que dá para conferir no Mercado Livre."""
    sugestoes = [_sugestao(s) for s in linha["sugestoes"]]
    return {
        "id": linha["id"], "titulo": linha["titulo"] or "(sem título)", "link": _link(linha),
        "situacao": formatos.situacao(linha["situacao"]),
        "visitas": formatos.milhar(linha["visitas"]), "vendas": formatos.milhar(linha["vendas"]),
        "qualidade": linha["qualidade"], "fotos": formatos.milhar(linha["fotos"]), "ficha": linha["ficha"],
        "sugestoes": sugestoes[:SUGESTOES_POR_ANUNCIO],
        "o_que_olhar": "" if sugestoes else linha["o_que_olhar"],
        "mais": max(len(sugestoes) - SUGESTOES_POR_ANUNCIO, 0),
    }


def _linha(linha):
    """Um anúncio na lista "Todos os anúncios"."""
    n = len(linha["sugestoes"])
    return {
        "id": linha["id"], "titulo": linha["titulo"] or "(sem título)", "link": _link(linha),
        "preco": formatos.dinheiro(linha["preco"]) if linha["preco"] is not None else "?",
        "estoque": formatos.milhar(linha["estoque"]),
        "visitas": formatos.milhar(linha["visitas"]), "vendas": formatos.milhar(linha["vendas"]),
        "sem_vendas": linha["vendas"] == 0, "situacao": formatos.situacao(linha["situacao"]),
        "mudancas": _plural(n, "mudança", "mudanças") if n else "",
    }


def _filtro(anuncios, busca, situacao, endereco):
    """A busca e o filtro de "Todos os anúncios", que funcionam sem JavaScript (formulário GET)."""
    contagem = {s: sum(1 for a in anuncios if a["situacao"] == s) for s in analise.ORDEM}
    achados = filtro.filtrar(anuncios, busca, situacao)
    quantos = ""
    if busca or situacao:
        quantos = (f"Mostrando {formatos.milhar(len(achados))} de {_plural(len(anuncios), 'anúncio', 'anúncios')}."
                   if achados else "Nenhum anúncio com essa busca.")
    return {
        "endereco": endereco, "busca": busca, "max_busca": filtro.MAX_BUSCA,
        "opcoes": [{"valor": s, "nome": formatos.situacao(s)["nome"], "quantos": n, "escolhida": s == situacao}
                   for s, n in contagem.items() if n or s == situacao],
        "quantos": quantos, "filtrando": bool(busca or situacao),
    }, achados


def formulario(sessao, aviso="", em_andamento=None):
    """prontos: os relatórios desta sessão que já terminaram, do mais novo para o mais antigo."""
    prontos = sorted((r for r in sessao["relatorios"].values() if r.estado == PRONTO and r.gerado_em),
                     key=lambda r: r.gerado_em, reverse=True)
    return {"apelido": sessao["usuario"].get("apelido") or "", "opcoes_dias": OPCOES_DIAS,
            "aviso": aviso, "em_andamento": em_andamento,
            "prontos": [{"id": r.id, "dias": r.dias, "quando": formatos.data_hora(r.gerado_em),
                         "anuncios": _plural(len(r.linhas), "anúncio", "anúncios")} for r in prontos]}


def andamento(relatorio):
    return {"relatorio": relatorio, "pct": relatorio.pct(), "etapas": relatorio.etapas(),
            "passos": len(PASSOS)}


def resultado(relatorio, sessao, ver_mudancas=None, busca="", situacao=""):
    """ver_mudancas: endereço da comparação com o relatório anterior do histórico, quando existe."""
    linhas = relatorio.linhas
    visitas = sum(l["visitas"] for l in linhas if l["visitas"] is not None)
    tem_vendas = any(l["vendas"] is not None for l in linhas)
    vendas = sum(l["vendas"] for l in linhas if l["vendas"] is not None)
    conversao = vendas / visitas if (visitas and tem_vendas) else None
    com_problema = analise.PROBLEMA_DE_VENDA | analise.PROBLEMA_DE_VISITA
    prioridade = [l for l in linhas if l["sugestoes"] or l["situacao"] in com_problema][:MAX_PRIORIDADES]
    n_mudancas = sum(len(l["sugestoes"]) for l in linhas)
    n_com_mudanca = sum(1 for l in linhas if l["sugestoes"])
    lista, achados = _filtro(linhas, busca, situacao, f"/relatorio/{relatorio.id}")
    return {
        "relatorio": relatorio, "apelido": sessao["usuario"].get("apelido") or "", "opcoes_dias": OPCOES_DIAS,
        # Os termos do Mercado Livre (5.3) pedem que o aplicativo diga quando os dados foram atualizados.
        "gerado_em": formatos.data_hora(relatorio.gerado_em) if relatorio.gerado_em else "",
        "quando": formatos.quando(relatorio.gerado_em) if relatorio.gerado_em else "",
        "ver_mudancas": ver_mudancas,
        "kpis": {
            "visitas": formatos.milhar(visitas), "por_dia": formatos.decimal(visitas / relatorio.dias),
            "vendas": formatos.milhar(vendas) if tem_vendas else "?",
            "conversao": f"{formatos.decimal(100 * conversao, 2)}%" if conversao is not None else "?",
            "conversao_baixa": conversao is not None and conversao < analise.CONVERSAO_BAIXA,
            "limite": f"{formatos.decimal(100 * analise.CONVERSAO_BAIXA, 0)}%",
            "mudancas": formatos.milhar(n_mudancas), "n_mudancas": n_mudancas, "uma_mudanca": n_mudancas == 1,
            "com_mudanca": _plural(n_com_mudanca, "anúncio", "anúncios"),
        },
        "pendencias": [{"valor": s, "texto": _plural(n, "anúncio", "anúncios"), **formatos.situacao(s),
                        "icone": ICONES_PENDENCIA[formatos.situacao(s)["classe"]]}
                       for s in analise.ORDEM if s in com_problema
                       for n in [sum(1 for l in linhas if l["situacao"] == s)] if n],
        "prioridade": [_cartao(l) for l in prioridade],
        "lista": lista, "anuncios": [_linha(l) for l in achados], "total": len(linhas),
    }


def _cartao_guardado(r, atual_id=None, mais_recente=False):
    quando = formatos.data_hora(r["criado_em"])
    local = datas.em_brasilia(r["criado_em"])
    return {
        "id": r["id"], "atual": r["id"] == atual_id, "mais_recente": mais_recente,
        "rotulo": f"Relatório de {quando}, {r['dias']} dias, {_plural(r['total'], 'anúncio', 'anúncios')}",
        "dia": formatos.dia_e_mes(r["criado_em"]), "ano_hora": f"{local:%Y} · {local:%H:%M}",
        "meta": f"{r['dias']} dias · {_plural(r['total'], 'anúncio', 'anúncios')}",
        "barra": formatos.barra(r["resumo"], r["total"]),
    }


def historico(lista, atual_id=None):
    """A linha do tempo: um cartão por relatório guardado, do mais novo para o mais antigo."""
    return {"cartoes": [_cartao_guardado(r, atual_id, i == 0) for i, r in enumerate(lista)],
            "quantos": _plural(len(lista), "relatório guardado", "relatórios guardados")}


def _antes_agora(antes, agora):
    return {"antes": formatos.milhar(antes), "agora": formatos.milhar(agora),
            "diferenca": formatos.diferenca(antes, agora), "mudou": antes != agora}


def historico_relatorio(dados, comparacao, lista, busca="", situacao=""):
    """Um relatório guardado. comparacao: o que comparacao.comparar() devolve, ou None se não há anterior."""
    antes = comparacao["antes"] if comparacao else {}
    local = datas.em_brasilia(dados["criado_em"])
    lista_filtro, achados = _filtro(dados["anuncios"], busca, situacao, f"/historico/{dados['id']}")
    mudou = None
    if comparacao is not None:
        mudou = {
            "anterior_id": comparacao["anterior"]["id"],
            "anterior_em": formatos.data_hora(comparacao["anterior"]["criado_em"], juntar=" "),
            "visitas": _antes_agora(*comparacao["visitas"]), "vendas": _antes_agora(*comparacao["vendas"]),
            "contas": [(len(comparacao["mudaram_de_situacao"]), "Mudaram de situação"),
                       (len(comparacao["novos"]), "Novos neste relatório"),
                       (len(comparacao["sairam"]), "Não estão mais no relatório"),
                       (comparacao["titulos_mudaram"], "Títulos que mudaram")],
            "mudaram": [{"titulo": a["titulo"] or "(sem título)",
                         "antes": formatos.situacao(antes[a["id"]]["situacao"]),
                         "agora": formatos.situacao(a["situacao"]),
                         "visitas": _antes_agora(antes[a["id"]]["visitas"], a["visitas"]),
                         "vendas": _antes_agora(antes[a["id"]]["vendas"], a["vendas"])}
                        for a in comparacao["mudaram_de_situacao"]],
            "novos": [{"titulo": a["titulo"] or "(sem título)", "situacao": formatos.situacao(a["situacao"])}
                      for a in comparacao["novos"]],
            "sairam": [a["titulo"] or "(sem título)" for a in comparacao["sairam"]],
        }
    anuncios = []
    for a in achados:
        anterior = antes.get(a["id"])
        anuncios.append({
            "titulo": a["titulo"] or "(sem título)", "situacao": formatos.situacao(a["situacao"]),
            "titulo_antes": ((anterior["titulo"] or "(sem título)")
                             if anterior and anterior["titulo"] != a["titulo"] else ""),
            "novo": comparacao is not None and anterior is None,
            "situacao_antes": (formatos.situacao(anterior["situacao"])["nome"]
                               if anterior and anterior["situacao"] != a["situacao"] else ""),
            "visitas": _antes_agora(anterior["visitas"] if anterior else a["visitas"], a["visitas"]),
            "vendas": _antes_agora(anterior["vendas"] if anterior else a["vendas"], a["vendas"]),
        })
    return {
        **historico(lista, dados["id"]),
        "dados": dados, "dia": formatos.dia_e_mes(dados["criado_em"]), "ano": f"{local:%Y}",
        "meta": (f"Feito às {local:%H:%M} · últimos {dados['dias']} dias · "
                 f"{_plural(dados['total'], 'anúncio', 'anúncios')}"),
        "barra": formatos.barra(dados["resumo"], dados["total"]),
        "legenda": [{"nome": formatos.situacao(s)["nome"], "classe": formatos.situacao(s)["classe"], "quantos": n}
                    for s, n in dados["resumo"].items() if n or s != "SEM DADOS"],
        "mudou": mudou, "lista": lista_filtro, "anuncios": anuncios,
    }


def contagens(dados):
    """A página /contagens: só números, nenhuma conta, apelido ou anúncio."""
    totais = {nome: str(total) for (nome, _), (_, total) in zip(dados["colunas"], dados["totais"])}
    if dados["sem_erro"]:
        s = dados["sem_erro"]
        totais["relatorios_prontos"] = f"{s['prontos']} de {s['feitos']} ({s['pct']}%)"
    return {
        **dados,
        "itens": [(rotulo, totais[nome]) for nome, rotulo in dados["colunas"]],
        "desde_texto": formatos.dia(dados["desde"]) if dados["desde"] else "",
        "linhas": [(formatos.dia(d), valores) for d, valores in dados["dias"]],
    }
