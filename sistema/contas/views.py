"""Entrar com a conta do Mercado Livre, voltar de lá, sair, ver a conta e apagar tudo."""

import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.middleware.csrf import rotate_token
from django.shortcuts import redirect, render
from publico.paginas import com_login, erro, so_metodo, ver_outra
from relatorios import contagens, datas, formatos
from relatorios.historico import HISTORICO

from . import acesso, login, sessoes
from .models import Conta

APAGADA = "Apagamos a sua conta no Orzy, o acesso guardado e todo o histórico. Para usar de novo, é só conectar."
APAGADA_SEM_O_MERCADO_LIVRE = ("Apagamos a sua conta no Orzy, o acesso guardado e todo o histórico. Não consegui tirar "
                               "a permissão do Orzy no Mercado Livre agora: se quiser, tire por lá. O Orzy não guarda "
                               "mais nada da sua conta.")


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


@so_metodo("GET")
@com_login
def conta(request, sessao):
    """O que o Orzy guarda da conta e o "Desconectar e apagar tudo"."""
    usuario = sessao["usuario"]
    guardada = Conta.objects.filter(ml_user_id=usuario["id"]).first()
    return render(request, "contas/conta.html", {
        "apelido": usuario.get("apelido") or "",
        "numero": usuario["id"],
        "criada_em": formatos.dia(datas.hoje(guardada.criada_em)) if guardada else "",
        "conectada_em": formatos.data_hora(guardada.conectada_em) if guardada else "",
        "com_acesso": bool(guardada and guardada.acesso),
        "acesso_salvo_em": formatos.data_hora(guardada.acesso_salvo_em) if guardada and guardada.acesso else "",
        "relatorios": formatos.milhar(guardada.relatorios.count() if guardada else 0),
        "dias_sem_acesso": acesso.DIAS_SEM_ACESSO,
    })


@so_metodo("POST")
@com_login
def apagar(request, sessao):
    if request.POST.get("confirmo") != "on":
        return erro(request, "Confirme que quer desconectar e apagar tudo.", status=400)
    cliente = sessao["cliente"]
    tokens = getattr(cliente, "tokens", None) or {}
    valido = tokens.get("access_token") if tokens.get("expira_em", 0) > time.time() else None
    confirmou = acesso.desconectar(sessao["usuario"]["id"], token_da_sessao=valido)
    request.session.flush()  # a sessão já saiu da memória (todas as da conta); aqui sai também o cookie
    return ver_outra("/conta/apagada" if confirmou else "/conta/apagada?mercado-livre=nao")


@so_metodo("GET")
def apagada(request):
    mensagem = APAGADA if request.GET.get("mercado-livre") != "nao" else APAGADA_SEM_O_MERCADO_LIVRE
    return erro(request, mensagem, status=200, titulo="Conta apagada")
