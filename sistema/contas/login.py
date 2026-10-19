"""Entrar com a conta do Mercado Livre (OAuth com PKCE).

O Client Secret é usado só aqui, no servidor. O token de acesso fica na sessão, na memória.
O refresh token não é guardado: quando o token de acesso vence, a pessoa entra de novo.
"""

import logging
import secrets

import ml_api

MENSAGEM_LOGIN_FALHOU = "Não consegui concluir o login com o Mercado Livre. Tente de novo em alguns minutos."


class ErroLoginSite(Exception):
    """Mensagem para mostrar à pessoa, em português e sem detalhes técnicos."""


class ClienteDaSessao(ml_api.ClienteML):
    """Login só na memória: não renova sozinho. Quando o token vence, a pessoa entra de novo."""

    _mensagem_login = "Seu login com o Mercado Livre venceu. Clique em Conectar de novo."

    def _renovar(self):
        raise ml_api.ErroLogin(self._mensagem_login)


def iniciar(config, sessao):
    """Passo 1: devolve o endereço do Mercado Livre onde a pessoa autoriza o acesso."""
    verificador, desafio = ml_api.gerar_pkce()
    estado = secrets.token_urlsafe(24)
    sessao["login_pendente"] = {"estado": estado, "verificador": verificador}
    return ml_api.montar_url_autorizacao(config.app_ml(), estado, desafio)


def concluir(config, sessao, parametros):
    """Passo 2: o Mercado Livre devolve a pessoa para /retorno com um código. Troca o código pelo login.

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
        tokens.pop("refresh_token", None)  # o site não guarda o refresh token
        cliente = ClienteDaSessao(config.app_ml(), tokens)
        eu = cliente.obter_usuario()
    except ml_api.ErroML as e:
        logging.warning("Login com o Mercado Livre não concluído: %s", e)
        raise ErroLoginSite(MENSAGEM_LOGIN_FALHOU) from None
    if not eu or not eu.get("id"):
        raise ErroLoginSite(MENSAGEM_LOGIN_FALHOU)
    return cliente, {"id": eu["id"], "apelido": eu.get("nickname") or ""}
