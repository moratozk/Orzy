"""Peças comuns das páginas: só o método certo, a página de erro e o redirecionamento depois de um formulário."""

import functools

from django.http import HttpResponseRedirect
from django.shortcuts import render

NAO_ENCONTRADO = "Não encontrei essa página."


def erro(request, mensagem, status, codigo=None):
    """A página de erro do visual novo. codigo: o número acima do título ("Erro 404"); sem ele, não aparece."""
    return render(request, "publico/erro.html", {"mensagem": mensagem, "codigo": codigo}, status=status)


def nao_encontrado(request):
    return erro(request, NAO_ENCONTRADO, status=404, codigo=404)


def so_metodo(*metodos):
    """A página só responde a estes métodos (quem aceita GET aceita HEAD). Os outros recebem o 404 de endereço
    errado, como no site de antes."""
    aceitos = set(metodos) | ({"HEAD"} if "GET" in metodos else set())

    def decorador(view):
        @functools.wraps(view)
        def envolvida(request, *args, **kwargs):
            if request.method not in aceitos:
                return nao_encontrado(request)
            return view(request, *args, **kwargs)
        return envolvida
    return decorador


def ver_outra(destino):
    """Depois de um formulário (POST), o navegador abre a página nova com GET: recarregar não envia de novo."""
    resposta = HttpResponseRedirect(destino)
    resposta.status_code = 303
    return resposta
