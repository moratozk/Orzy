"""Entrar com a conta do Mercado Livre, voltar de lá e sair."""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.middleware.csrf import rotate_token
from django.shortcuts import redirect

from publico.paginas import erro, so_metodo
from relatorios import contagens
from relatorios.historico import HISTORICO

from . import login, sessoes


@so_metodo("GET")
def entrar(request):
    request.session.flush()  # quem já tinha uma sessão neste navegador começa outra: a de antes deixa de valer
    return HttpResponseRedirect(login.iniciar(settings.ORZY, request.session))


@so_metodo("GET")
def retorno(request):
    if not request.session.keys():
        return erro(request, "Sua sessão expirou. Clique em Conectar de novo para entrar.", status=400)
    try:
        cliente, usuario = login.concluir(settings.ORZY, request.session, request.GET)
    except login.ErroLoginSite as e:
        return erro(request, str(e), status=400)
    contagens.contar(HISTORICO, logins=1)
    # Código novo depois do login: quem soubesse o código de antes (o do /entrar) não entra na conta.
    request.session.cycle_key()
    rotate_token(request)
    request.session.update({"cliente": cliente, "usuario": usuario, "relatorios": {}})
    sessoes.marcar_login(request.session)
    return redirect("/relatorio")


@so_metodo("POST")
def sair(request):
    request.session.flush()
    return redirect("/")
