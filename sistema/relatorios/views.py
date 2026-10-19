"""Relatório e histórico. Todas as páginas pedem login: quem não tem volta para a página inicial."""

import functools
import logging

import meus_anuncios
from contas.sessoes import logada
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from publico.paginas import erro, nao_encontrado, so_metodo, ver_outra

from . import busca, comparacao, contagens, telas
from .geracao import ERRO, GERANDO, PRONTO, RELATORIOS, ErroRelatorio, dias_pedidos, em_andamento
from .historico import HISTORICO


def com_login(view):
    """Passa a sessão para a página, ou manda para a página inicial quem não entrou com o Mercado Livre."""
    @functools.wraps(view)
    def envolvida(request, *args, **kwargs):
        sessao = logada(request)
        if sessao is None:
            return redirect("/")
        return view(request, sessao, *args, **kwargs)
    return envolvida


def _relatorio_da_sessao(request, relatorio_id):
    sessao = logada(request)
    return sessao["relatorios"].get(relatorio_id) if sessao is not None else None


# ------------------------------------------------------------ relatórios

@so_metodo("GET")
@com_login
def formulario(request, sessao):
    return render(request, "relatorios/formulario.html",
                  telas.formulario(sessao, em_andamento=em_andamento(sessao)))


@so_metodo("POST")
@com_login
def gerar(request, sessao):
    try:
        relatorio = RELATORIOS.iniciar(sessao, dias_pedidos(request.POST.get("dias")))
    except ErroRelatorio as e:
        return render(request, "relatorios/formulario.html",
                      telas.formulario(sessao, aviso=str(e), em_andamento=em_andamento(sessao)))
    return ver_outra(f"/relatorio/{relatorio.id}")


@so_metodo("GET")
def ver(request, relatorio_id):
    relatorio = _relatorio_da_sessao(request, relatorio_id)
    if relatorio is None:
        return nao_encontrado(request)
    if relatorio.estado == GERANDO:
        return render(request, "relatorios/andamento.html", telas.andamento(relatorio))
    if relatorio.estado == ERRO:
        return render(request, "relatorios/com_erro.html", {"relatorio": relatorio})
    return render(request, "relatorios/resultado.html",
                  telas.resultado(relatorio, request.session, _endereco_das_mudancas(relatorio),
                                  *busca.ler(request.GET)))


def _endereco_das_mudancas(relatorio):
    """Onde ver o que mudou desde o relatório anterior, se este foi guardado e há um anterior para comparar."""
    if relatorio.historico_id is None:
        return None
    try:
        anterior = HISTORICO.id_do_anterior(relatorio.ml_user_id, relatorio.historico_id)
    except Exception:  # o resultado já está na memória: um problema no histórico não o esconde
        logging.exception("Não consegui procurar o relatório anterior no histórico")
        return None
    return f"/historico/{relatorio.historico_id}#mudancas" if anterior is not None else None


@so_metodo("GET")
def andamento(request, relatorio_id):
    relatorio = _relatorio_da_sessao(request, relatorio_id)
    if relatorio is None:
        return nao_encontrado(request)
    return JsonResponse(relatorio.para_json(), json_dumps_params={"ensure_ascii": False})


@so_metodo("GET")
def planilha(request, relatorio_id):
    relatorio = _relatorio_da_sessao(request, relatorio_id)
    if relatorio is None or relatorio.estado != PRONTO:
        return nao_encontrado(request)
    texto = meus_anuncios.montar_csv(relatorio.linhas, relatorio.dias)
    resposta = HttpResponse(("﻿" + texto).encode("utf-8"), content_type="text/csv; charset=utf-8")
    resposta["Content-Disposition"] = f'attachment; filename="orzy-anuncios-{relatorio.dias}-dias.csv"'
    return resposta


# ------------------------------------------------------------ histórico

@so_metodo("GET")
@com_login
def historico(request, sessao):
    """Abre no relatório guardado mais recente; quem ainda não tem nenhum vê a página vazia."""
    conta = sessao["usuario"]["id"]
    lista = HISTORICO.listar(conta)
    if not lista:
        return render(request, "relatorios/historico.html")
    return _guardado(request, conta, lista[0]["id"], lista)


@so_metodo("GET")
@com_login
def ver_historico(request, sessao, guardado_id):
    conta = sessao["usuario"]["id"]
    return _guardado(request, conta, guardado_id, HISTORICO.listar(conta))


def _guardado(request, conta, guardado_id, lista):
    """Um relatório guardado, com o que mudou desde o anterior do mesmo período."""
    dados = HISTORICO.ver(conta, guardado_id)
    if dados is None:
        return nao_encontrado(request)
    anterior_id = HISTORICO.id_do_anterior(conta, dados["id"])
    anterior = HISTORICO.ver(conta, anterior_id) if anterior_id is not None else None
    mudancas = comparacao.comparar(anterior, dados) if anterior is not None else None
    return render(request, "relatorios/historico_relatorio.html",
                  telas.historico_relatorio(dados, mudancas, lista, *busca.ler(request.GET)))


@so_metodo("POST")
@com_login
def apagar_historico(request, sessao):
    if request.POST.get("confirmo") != "on":
        return erro(request, "Confirme que quer apagar o histórico.", status=400)
    HISTORICO.apagar(sessao["usuario"]["id"])
    # Tira da sessão os relatórios já prontos; um que ainda está sendo gerado continua até terminar.
    sessao["relatorios"] = {i: r for i, r in sessao["relatorios"].items() if r.estado == GERANDO}
    return ver_outra("/historico")


# ------------------------------------------------------------ contagens do beta

@so_metodo("GET")
def contagens_do_beta(request):
    sessao = logada(request)
    # Para quem não está em ORZY_CONTAS_ADMIN, a página não existe: o mesmo 404 de um endereço errado.
    if sessao is None or int(sessao["usuario"]["id"]) not in settings.ORZY.contas_admin:
        return nao_encontrado(request)
    dados = contagens.resumo(HISTORICO, RELATORIOS.max_anuncios)
    return render(request, "relatorios/contagens.html", telas.contagens(dados))
