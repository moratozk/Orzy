"""O acesso guardado de cada conta: salvar no Conectar, renovar um de cada vez, perder e apagar.

O código de renovação (refresh token) do Mercado Livre é de uso único: cada renovação devolve um novo e o de antes
deixa de valer. Por isso:
- só um renova de cada vez em cada conta: a linha da conta fica travada no banco (select_for_update) do começo da
  renovação até o código novo estar salvo. Quem chega no meio espera e renova com o código novo;
- o código novo é salvo antes de qualquer outra coisa: o token de acesso novo só sai daqui depois de o banco confirmar.

Quando o Mercado Livre recusa o código guardado (invalid_grant: a pessoa tirou a permissão do Orzy, trocou a senha ou o
código venceu), o Orzy apaga o acesso guardado na hora e encerra as sessões da conta. A conta e o histórico esperam a
pessoa conectar de novo por DIAS_SEM_ACESSO dias e depois saem (apagar_sem_acesso, uma vez por dia). O Mercado Livre
não avisa quando alguém tira a permissão, e trocar a senha dá o mesmo erro: por isso a espera, em vez de apagar o
histórico de quem só trocou a senha. "Desconectar e apagar tudo" apaga na hora e também tira a permissão do Orzy no
Mercado Livre.
"""

import logging
from datetime import timedelta

import ml_api
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from relatorios import datas

from . import cofre
from .models import Conta
from .sessoes import GUARDADAS

DIAS_SEM_ACESSO = 30  # conta sem acesso guardado e sem conectar por esse tempo sai com tudo o que é dela
HORAS_ENTRE_CONFERENCIAS = 20  # a conferência de todo dia renova quem não renovou nesse tempo

MENSAGEM_SEM_ACESSO = "O Mercado Livre não aceita mais o acesso do Orzy à sua conta. Clique em Conectar de novo."
MENSAGEM_NAO_RENOVOU = "Não consegui renovar o acesso com o Mercado Livre agora. Tente de novo em alguns minutos."


class SemAcesso(ml_api.ErroLogin):
    """A conta não tem (ou deixou de ter) acesso guardado: a pessoa precisa clicar em Conectar de novo."""


def guardar(ml_user_id, apelido, codigo_de_renovacao):
    """No Conectar: cria a conta, ou atualiza a que já existe, com o acesso novo cifrado.

    Sem o código de renovação (o app do Mercado Livre sem o fluxo Refresh Token), a conta nova fica sem acesso guardado
    e a que já existe fica com o acesso que tinha.
    """
    agora = datas.agora()
    campos = ["apelido", "conectada_em"]
    if codigo_de_renovacao:
        acesso = cofre.fechar(settings.ORZY.chave_acesso, ml_user_id, codigo_de_renovacao)
        salvo_em, sem_acesso_desde = agora, None
        campos += ["acesso", "acesso_salvo_em", "sem_acesso_desde"]
    else:
        logging.error("O Mercado Livre não mandou o código de renovação no login: confira se o app tem o fluxo "
                      "Refresh Token. A conta fica sem acesso guardado.")
        acesso, salvo_em, sem_acesso_desde = "", None, agora
    # Um comando só no banco (INSERT ... ON CONFLICT DO UPDATE): dois logins da mesma conta ao mesmo tempo não criam
    # duas contas, e uma renovação em andamento termina antes (a linha está travada).
    Conta.objects.bulk_create(
        [Conta(ml_user_id=ml_user_id, apelido=apelido, criada_em=agora, conectada_em=agora, acesso=acesso,
               acesso_salvo_em=salvo_em, sem_acesso_desde=sem_acesso_desde)],
        update_conflicts=True, unique_fields=["ml_user_id"], update_fields=campos)


def renovar(ml_user_id, so_se_salvo_antes_de=None):
    """Renova o acesso com o código de renovação guardado e devolve o login novo, sem o código de renovação.

    Devolve só depois de o código novo estar salvo. so_se_salvo_antes_de: na conferência de todo dia, só renova se o
    acesso foi salvo antes desse momento (outro pode ter renovado agora há pouco); senão devolve None.
    """
    chave = settings.ORZY.chave_acesso
    perdeu = False
    with transaction.atomic():
        conta = Conta.objects.select_for_update().filter(ml_user_id=ml_user_id).first()
        if conta is None or not conta.acesso:
            raise SemAcesso(MENSAGEM_SEM_ACESSO)
        if so_se_salvo_antes_de and conta.acesso_salvo_em and conta.acesso_salvo_em >= so_se_salvo_antes_de:
            return None
        try:
            codigo = cofre.abrir(chave, conta.ml_user_id, conta.acesso)
        except cofre.ErroCofre as e:
            # Chave trocada ou valor estragado: não é a pessoa que tirou a permissão. A conta fica como está; conectar
            # de novo guarda um acesso novo.
            logging.error("O acesso guardado de uma conta não abriu: %s", e)
            raise ml_api.ErroLogin(MENSAGEM_SEM_ACESSO) from None
        try:
            tokens = ml_api.renovar_token(settings.ORZY.app_ml(), {"refresh_token": codigo, "user_id": ml_user_id},
                                          gravar=False)
        except ml_api.ErroML as e:
            if e.codigo != "invalid_grant":
                # Sem internet, Mercado Livre fora do ar, Client Secret trocado: o código guardado continua valendo.
                logging.warning("Não consegui renovar o acesso de uma conta: %s", e)
                raise ml_api.ErroLogin(MENSAGEM_NAO_RENOVOU, e.status, e.codigo) from None
            conta.acesso, conta.sem_acesso_desde = "", datas.agora()
            conta.save(update_fields=["acesso", "sem_acesso_desde"])
            perdeu = True
        else:
            conta.acesso = cofre.fechar(chave, conta.ml_user_id, tokens.pop("refresh_token"))
            conta.acesso_salvo_em = datas.agora()
            conta.save(update_fields=["acesso", "acesso_salvo_em"])
    if perdeu:
        logging.info("O Mercado Livre recusou o acesso guardado de uma conta: o acesso foi apagado.")
        GUARDADAS.encerrar_da_conta(ml_user_id)
        raise SemAcesso(MENSAGEM_SEM_ACESSO)
    return tokens


def desconectar(ml_user_id, token_da_sessao=None):
    """"Desconectar e apagar tudo": apaga a conta e tudo o que é dela (o acesso guardado e o histórico), encerra as
    sessões dela em todos os navegadores e pede ao Mercado Livre para tirar a permissão do Orzy.

    Devolve True se o Mercado Livre confirmou. Se ele não confirmar, o Orzy já apagou tudo do lado dele mesmo assim.
    """
    codigo = None
    with transaction.atomic():
        conta = Conta.objects.select_for_update().filter(ml_user_id=ml_user_id).first()
        if conta is not None:
            if conta.acesso:
                try:
                    codigo = cofre.abrir(settings.ORZY.chave_acesso, conta.ml_user_id, conta.acesso)
                except cofre.ErroCofre as e:
                    logging.error("O acesso guardado de uma conta não abriu ao apagar a conta: %s", e)
            conta.delete()  # o histórico sai junto, pelo banco
    GUARDADAS.encerrar_da_conta(ml_user_id)
    return _tirar_permissao(ml_user_id, token_da_sessao, codigo)


def _tirar_permissao(ml_user_id, token_da_sessao, codigo):
    """Tenta com o token de acesso da sessão e, se não der, com um novo, do código de renovação que estava guardado."""
    app = settings.ORZY.app_ml()
    erro = None
    if token_da_sessao:
        try:
            ml_api.tirar_permissao(app, token_da_sessao, ml_user_id)
            return True
        except ml_api.ErroML as e:
            erro = e
    if codigo:
        try:
            novo = ml_api.renovar_token(app, {"refresh_token": codigo}, gravar=False)
            ml_api.tirar_permissao(app, novo["access_token"], ml_user_id)
            return True
        except ml_api.ErroML as e:
            erro = e
    if erro is not None:
        logging.warning("Não consegui tirar a permissão do Orzy no Mercado Livre ao apagar uma conta: %s", erro)
    return False


def conferir_todos():
    """Uma vez por dia: renova o acesso de cada conta que não renovou nas últimas horas. O código de renovação não
    chega a vencer (vale 6 meses), e o Orzy percebe quem tirou a permissão no Mercado Livre.

    Devolve quantas contas renovaram, quantas perderam o acesso e quantas deram outro erro (tentam de novo amanhã).
    """
    limite = datas.agora() - timedelta(hours=HORAS_ENTRE_CONFERENCIAS)
    numeros = list(Conta.objects.exclude(acesso="")
                   .filter(Q(acesso_salvo_em__lt=limite) | Q(acesso_salvo_em=None))
                   .values_list("ml_user_id", flat=True))
    renovadas = perdidas = falhas = 0
    for numero in numeros:
        try:
            if renovar(numero, so_se_salvo_antes_de=limite) is not None:
                renovadas += 1
        except SemAcesso:
            perdidas += 1
        except ml_api.ErroML:
            falhas += 1  # renovar() já deixou a linha no registro
        except Exception:
            falhas += 1
            logging.exception("Falha inesperada ao conferir o acesso de uma conta")
    return renovadas, perdidas, falhas


def apagar_sem_acesso(dias=DIAS_SEM_ACESSO):
    """Apaga as contas que estão sem acesso guardado há mais de `dias` dias e que não conectaram nesse tempo, com
    tudo o que é delas. Devolve quantas."""
    limite = datas.agora() - timedelta(days=dias)
    velhas = Conta.objects.filter(acesso="", conectada_em__lt=limite).exclude(sem_acesso_desde__gte=limite)
    apagadas = 0
    for numero in list(velhas.values_list("ml_user_id", flat=True)):
        with transaction.atomic():
            # Confere de novo com a linha travada: quem conectou agora há pouco fica.
            conta = velhas.select_for_update().filter(ml_user_id=numero).first()
            if conta is None:
                continue
            conta.delete()
        GUARDADAS.encerrar_da_conta(numero)
        apagadas += 1
    return apagadas
