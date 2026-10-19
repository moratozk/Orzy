"""Números, datas e situações do jeito que as páginas mostram: 2.417, 1,61%, 15/10/2026 às 20:21, "Visita sem venda".

Tudo em texto pronto, sem depender da configuração de idioma do Django. Datas no horário de Brasília.
"""

from . import datas

MESES = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")

# Situação do analise.py: nome na página e a classe de cor do visual novo (s-vsv, b-vsv...).
SITUACOES = {
    "VISITA SEM VENDA": ("Visita sem venda", "vsv"),
    "CONVERTE POUCO": ("Converte pouco", "cp"),
    "POUCA VISITA": ("Pouca visita", "pv"),
    "VENDE, MAS POUCO VISTO": ("Vende, mas pouco visto", "vpv"),
    "VENDENDO BEM": ("Vendendo bem", "vb"),
    "SEM DADOS": ("Sem dados", "sd"),
}
# Prioridade do anúncio pela situação (as barrinhas ao lado da situação): vende pouco para o que é visto, depois
# quase não é visto, depois está bem.
PRIORIDADES = {"vsv": 3, "cp": 3, "pv": 2, "vpv": 2, "vb": 1}
NOMES_PRIORIDADE = {3: "alta", 2: "média", 1: "baixa"}
# De que parte do anúncio é cada sugestão (o começo do tema no analise.py).
AREAS = {"titulo": "Título", "fotos": "Fotos", "ficha": "Ficha técnica", "frete": "Frete",
         "tipo": "Tipo de anúncio", "ml": "Mercado Livre"}


def milhar(valor):
    """2417 vira "2.417"; sem número, "?"."""
    if valor is None:
        return "?"
    return f"{round(valor):,}".replace(",", ".")


def decimal(valor, casas=1):
    """13.65 vira "13,7"."""
    if valor is None:
        return "?"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def dinheiro(valor):
    """59.9 vira "59,90" (o "R$" a página põe)."""
    return decimal(valor, 2)


def data_hora(momento, juntar=" às "):
    """15/10/2026 às 20:21, no horário de Brasília."""
    if momento is None:
        return "?"
    local = datas.em_brasilia(momento)
    return f"{local:%d/%m/%Y}{juntar}{local:%H:%M}"


def dia(data):
    """Uma data (sem hora) como 15/10/2026."""
    return f"{data:%d/%m/%Y}" if data is not None else "?"


def quando(momento):
    """"hoje, 20:21" ou "15/10, 20:21", no horário de Brasília."""
    local = datas.em_brasilia(momento)
    dia = "hoje" if local.date() == datas.hoje() else f"{local:%d/%m}"
    return f"{dia}, {local:%H:%M}"


def dia_e_mes(momento):
    """15 out, no horário de Brasília."""
    local = datas.em_brasilia(momento)
    return f"{local.day} {MESES[local.month - 1]}"


def situacao(nome):
    """{"nome": "Visita sem venda", "classe": "vsv", "prioridade": 3, "nome_prioridade": "alta",
    "barras": [True, True, True]} (as três barrinhas da prioridade, cheias ou não; nenhuma em "Sem dados")."""
    rotulo, classe = SITUACOES.get(nome, (nome.capitalize(), "sd"))
    prioridade = PRIORIDADES.get(classe, 0)
    return {"nome": rotulo, "classe": classe, "prioridade": prioridade,
            "nome_prioridade": NOMES_PRIORIDADE.get(prioridade, ""),
            "barras": [i < prioridade for i in range(3)] if prioridade else []}


def area(tema):
    return AREAS.get(tema.replace(":", "_").split("_")[0], "Anúncio")


def diferenca(antes, agora):
    """O que mudou num número: {"texto": "+30", "classe": "sobe"} ("−16" com o sinal de menos), ou None se não mudou
    ou falta um dos dois."""
    if antes is None or agora is None or antes == agora:
        return None
    texto = f"{agora - antes:+,d}".replace(",", ".").replace("-", "\u2212")
    return {"texto": texto, "classe": "sobe" if agora > antes else "desce"}


def barra(resumo, total):
    """As fatias da barra de situações (SVG de 0 a 100): classe, x e largura, com um vão entre elas.

    Números calculados aqui, em texto com ponto, para irem direto aos atributos do SVG.
    """
    fatias, x = [], 0.0
    for nome, quantos in resumo.items():
        if not quantos or not total:
            continue
        largura = 100 * quantos / total
        fatias.append({"classe": SITUACOES.get(nome, ("", "sd"))[1], "x": f"{x:.2f}",
                       "largura": f"{max(largura - 0.8, 0.4):.2f}"})
        x += largura
    return fatias
