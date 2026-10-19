"""Páginas públicas (início, textos legais, robots.txt) e as páginas de erro."""

import analise
from contas.sessoes import logada
from django.http import HttpResponse
from django.shortcuts import redirect, render
from relatorios.geracao import OPCOES_DIAS, RELATORIOS

from . import legal
from .paginas import NAO_ENCONTRADO, erro, so_metodo

# Robôs de busca ficam nas páginas públicas: as outras pedem login e só ligariam o servidor à toa.
ROBOTS = "User-agent: *\nDisallow: /entrar\nDisallow: /retorno\nDisallow: /relatorio\nDisallow: /historico\n"
ERRO_INTERNO = "Algo deu errado do nosso lado. Tente de novo em alguns minutos."
RECUSADO = "Pedido recusado. Volte à página e tente de novo."


def _dias_em_texto(opcoes):
    """(30, 60, 90, 150) vira "30, 60, 90 ou 150"."""
    numeros = [str(d) for d in opcoes]
    return ", ".join(numeros[:-1]) + " ou " + numeros[-1] if len(numeros) > 1 else numeros[0]


@so_metodo("GET")
def inicio(request):
    """Os fatos da página saem da configuração e das regras (analise.py): a página acompanha qualquer ajuste."""
    return render(request, "publico/inicio.html", {
        "logado": logada(request) is not None,
        "max_anuncios": RELATORIOS.max_anuncios,
        "dias": _dias_em_texto(OPCOES_DIAS),
        "poucas_visitas": analise.POUCAS_VISITAS,
        "a_cada": round(1 / analise.CONVERSAO_BAIXA),  # 0.01 vira "1 venda a cada 100 visitas"
        "min_fotos": analise.MIN_FOTOS,
        "largura_zoom": analise.LARGURA_ZOOM,
    })


@so_metodo("GET")
def texto_legal(request, rota):
    return render(request, "publico/legal.html", {
        "rota": rota, "nome": legal.NOMES[rota], "documento": legal.carregar(rota),
        "outra": "termos" if rota == "privacidade" else "privacidade",
        "outro_nome": legal.NOMES["termos" if rota == "privacidade" else "privacidade"],
    })


@so_metodo("GET")
def robots(request):
    resposta = HttpResponse(ROBOTS, content_type="text/plain; charset=utf-8")
    resposta["Cache-Control"] = "public, max-age=86400"
    return resposta


@so_metodo("GET")
def saude(request):
    return HttpResponse("ok", content_type="text/plain; charset=utf-8")


def recusado(request, reason=""):
    """Pedido que muda algo e não veio de uma página do próprio site (o CSRF do Django recusou).

    Sem login, volta para a página inicial: é o caso de quem deixou a página aberta e a sessão acabou.
    """
    if logada(request) is None:
        return redirect("/")
    return erro(request, RECUSADO, status=403, codigo=403)


def pedido_invalido(request, exception=None):
    return erro(request, "Não entendi esse pedido. Volte à página e tente de novo.", status=400, codigo=400)


def proibido(request, exception=None):
    return erro(request, RECUSADO, status=403, codigo=403)


def nao_encontrado(request, exception=None):
    return erro(request, NAO_ENCONTRADO, status=404, codigo=404)


def erro_interno(request):
    return erro(request, ERRO_INTERNO, status=500, codigo=500)
