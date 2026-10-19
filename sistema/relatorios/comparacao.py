"""O que mudou entre dois relatórios guardados da mesma conta e do mesmo período.

Diz o que mudou, sem afirmar a causa nem garantir resultado (docs/03-decisoes-tecnicas.md): visitas e vendas mudam
por muitos motivos. O histórico guarda só número, título, visitas, vendas, situação e pontos de cada anúncio, então
é isso que dá para comparar.
"""


def _soma(anuncios, campo):
    return sum(a[campo] for a in anuncios if a[campo] is not None)


def comparar(anterior, atual):
    """anterior e atual: relatórios como Historico.ver() devolve, o anterior criado antes."""
    antes = {a["id"]: a for a in anterior["anuncios"]}
    agora = {a["id"] for a in atual["anuncios"]}
    return {
        "anterior": {"id": anterior["id"], "criado_em": anterior["criado_em"]},
        "antes": antes,  # cada anúncio como estava no relatório anterior, pelo número; os novos não estão aqui
        "mudaram_de_situacao": [a for a in atual["anuncios"]
                                if a["id"] in antes and antes[a["id"]]["situacao"] != a["situacao"]],
        "titulos_mudaram": sum(1 for a in atual["anuncios"]
                               if a["id"] in antes and antes[a["id"]]["titulo"] != a["titulo"]),
        "novos": [a for a in atual["anuncios"] if a["id"] not in antes],
        "sairam": [a for a in anterior["anuncios"] if a["id"] not in agora],
        "visitas": (_soma(anterior["anuncios"], "visitas"), _soma(atual["anuncios"], "visitas")),
        "vendas": (_soma(anterior["anuncios"], "vendas"), _soma(atual["anuncios"], "vendas")),
    }
