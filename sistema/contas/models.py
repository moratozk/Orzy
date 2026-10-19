"""A conta de cada vendedor no Orzy (fase 4, passo 2).

A conta é criada no primeiro "Conectar com Mercado Livre", sem senha. Guarda o número e o apelido da conta do Mercado
Livre, as datas e o acesso: o código de renovação (refresh token), cifrado com a chave que fica fora do banco
(cofre.py). O token de acesso de cada sessão continua só na memória. Tudo o que o Orzy guarda de um vendedor fica
pendurado na conta e sai junto com ela, pelo próprio banco (on_delete=DB_CASCADE): o histórico hoje, os dados
importados nos próximos passos.
"""

from django.db import models


class Conta(models.Model):
    ml_user_id = models.BigIntegerField(unique=True)  # o número da conta no Mercado Livre
    apelido = models.TextField(blank=True)  # o apelido no Mercado Livre, como veio no último Conectar
    criada_em = models.DateTimeField()  # o primeiro Conectar
    conectada_em = models.DateTimeField()  # o último Conectar
    acesso = models.TextField(blank=True)  # o código de renovação, cifrado (cofre.py); vazio: sem acesso guardado
    acesso_salvo_em = models.DateTimeField(null=True)  # quando o acesso foi salvo (no Conectar ou ao renovar)
    sem_acesso_desde = models.DateTimeField(null=True)  # quando o Mercado Livre deixou de aceitar o acesso guardado

    class Meta:
        ordering = ["id"]
