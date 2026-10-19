"""Entrar com a conta do Mercado Livre (OAuth com PKCE).

O Client Secret é usado só aqui, no servidor. O token de acesso fica na sessão, na memória. O código de renovação
(refresh token) vai para o banco, cifrado, na conta (acesso.py): quando o token de acesso vence, a sessão renova por lá.
"""

import logging
import secrets

import ml_api
from django.db import DatabaseError

from . import acesso

MENSAGEM_LOGIN_FALHOU = "Não consegui concluir o login com o Mercado Livre. Tente de novo em alguns minutos."


class ErroLoginSite(Exception):
    """Mensagem para mostrar à pessoa, em português e sem detalhes técnicos."""


class ClienteDaConta(ml_api.ClienteML):
    """O login da sessão, na memória. Quando o token de acesso vence (ou o Mercado Livre recusa antes da hora), renova
    com o acesso guardado da conta: um de cada vez, com o código novo salvo antes de usar (acesso.renovar)."""

    _mensagem_login = acesso.MENSAGEM_SEM_ACESSO

    def __init__(self, config, tokens, ml_user_id=None):
        super().__init__(config, tokens)
        self.ml_user_id = ml_user_id  # None enquanto a conta não foi salva: não renova

    def _renovar(self):
        if self.ml_user_id is None:
            raise ml_api.ErroLogin(self._mensagem_login)
        return acesso.renovar(self.ml_user_id)


def iniciar(config, sessao):
    """Passo 1: devolve o endereço do Mercado Livre onde a pessoa autoriza o acesso."""
    verificador, desafio = ml_api.gerar_pkce()
    estado = secrets.token_urlsafe(24)
    sessao["login_pendente"] = {"estado": estado, "verificador": verificador}
    return ml_api.montar_url_autorizacao(config.app_ml(), estado, desafio)


def concluir(config, sessao, parametros):
    """Passo 2: o Mercado Livre devolve a pessoa para /retorno com um código. Troca o código pelo login e cria a conta
    (ou atualiza a que já existe) com o acesso guardado.

    Devolve (cliente, usuário). O cliente só existe na sessão.
    """
    pendente = sessao.pop("login_pendente", None)
    if not pendente or parametros.get("state") != pendente["estado"]:
        raise ErroLoginSite("Esse link de entrada não é válido ou já foi usado. Clique em Conectar de novo.")
    if parametros.get("error"):
        raise ErroLoginSite("Você não autorizou o acesso. Se foi engano, clique em Conectar de novo.")
    codigo = parametros.get("code")
    if not codigo:
        raise ErroLoginSite("O Mercado Livre não devolveu o código de acesso. Clique em Conectar de novo.")
    try:
        tokens = ml_api.trocar_code_por_token(config.app_ml(), codigo, verifier=pendente["verificador"],
                                              gravar=False)
        renovacao = tokens.pop("refresh_token", None)  # vai para o banco, cifrado; nunca para a sessão
        cliente = ClienteDaConta(config.app_ml(), tokens)
        eu = cliente.obter_usuario()
        if not eu or not eu.get("id"):
            raise ErroLoginSite(MENSAGEM_LOGIN_FALHOU)
        usuario = {"id": eu["id"], "apelido": eu.get("nickname") or ""}
        acesso.guardar(usuario["id"], usuario["apelido"], renovacao)
    except ml_api.ErroML as e:
        logging.warning("Login com o Mercado Livre não concluído: %s", e)
        raise ErroLoginSite(MENSAGEM_LOGIN_FALHOU) from None
    except DatabaseError:
        logging.exception("Login com o Mercado Livre não concluído: não consegui salvar a conta")
        raise ErroLoginSite(MENSAGEM_LOGIN_FALHOU) from None
    cliente.ml_user_id = usuario["id"]
    return cliente, usuario
