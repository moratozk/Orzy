"""O cofre do acesso guardado: o código de renovação do Mercado Livre (refresh token) vai para o banco cifrado.

A cifra é AES-256-GCM, da biblioteca cryptography. A chave fica fora do banco, na variável de ambiente
ORZY_CHAVE_ACESSO (orzy/configuracao.py): quem copiar só o banco não abre nada. Cada valor guardado leva junto, sem
cifrar, a versão do formato e o número da chave (um resumo dela, que não deixa descobrir a chave). O número da conta do
Mercado Livre entra na conferência da cifra: um valor copiado para a linha de outra conta não abre.

Formato: v1:<número da chave>:<base64 de 12 bytes sorteados + a cifra com a conferência>.
"""

import base64
import binascii
import hashlib
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VERSAO = "v1"
TAMANHO_NONCE = 12  # bytes sorteados a cada cifra, como o GCM pede


class ErroCofre(Exception):
    """O valor guardado não abre: estragado, mexido ou de outra conta."""


class OutraChave(ErroCofre):
    """O valor foi guardado com outra chave: ORZY_CHAVE_ACESSO mudou. É configuração, não culpa da conta."""


def numero_da_chave(chave):
    return hashlib.sha256(b"orzy-chave-do-acesso:" + chave).hexdigest()[:8]


def _da_conta(ml_user_id):
    return f"orzy-acesso:{int(ml_user_id)}".encode("ascii")


def fechar(chave, ml_user_id, texto):
    """Cifra o texto para guardar na linha da conta."""
    nonce = os.urandom(TAMANHO_NONCE)
    cifra = AESGCM(chave).encrypt(nonce, texto.encode("utf-8"), _da_conta(ml_user_id))
    return ":".join((VERSAO, numero_da_chave(chave), base64.urlsafe_b64encode(nonce + cifra).decode("ascii")))


def abrir(chave, ml_user_id, guardado):
    """O texto de volta. ErroCofre se não abrir; OutraChave se foi guardado com outra chave."""
    partes = guardado.split(":")
    if len(partes) != 3 or partes[0] != VERSAO:
        raise ErroCofre("o acesso guardado está num formato desconhecido")
    if partes[1] != numero_da_chave(chave):
        raise OutraChave("o acesso foi guardado com outra chave (ORZY_CHAVE_ACESSO mudou?)")
    try:
        bruto = base64.urlsafe_b64decode(partes[2])
        texto = AESGCM(chave).decrypt(bruto[:TAMANHO_NONCE], bruto[TAMANHO_NONCE:], _da_conta(ml_user_id))
        return texto.decode("utf-8")
    except (InvalidTag, ValueError, binascii.Error):
        raise ErroCofre("o acesso guardado não confere: foi mexido ou é de outra conta") from None
