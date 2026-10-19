"""O que fica guardado no banco: o histórico dos relatórios e as contagens do beta.

Só o que a Política de Privacidade diz (seção 6): de cada relatório, a data, o período, o número da conta, quantos
anúncios e quantos em cada situação; de cada anúncio, o número, o título, as visitas, as vendas, a situação e a
pontuação das sugestões. Nada de token, preço, estoque, link ou dado de comprador. As contagens são só números por
dia, sem dizer de qual conta.
"""

from django.db import models


class RelatorioGuardado(models.Model):
    ml_user_id = models.BigIntegerField(db_index=True)  # o número da conta no Mercado Livre
    criado_em = models.DateTimeField(db_index=True)
    dias = models.PositiveSmallIntegerField()
    total = models.PositiveIntegerField()  # quantos anúncios
    resumo = models.JSONField()  # quantos anúncios em cada situação

    class Meta:
        ordering = ["id"]


class AnuncioGuardado(models.Model):
    relatorio = models.ForeignKey(RelatorioGuardado, on_delete=models.CASCADE, related_name="anuncios")
    item_id = models.CharField(max_length=40)
    titulo = models.TextField()
    visitas = models.IntegerField(null=True)  # vazio quando o Mercado Livre não respondeu
    vendas = models.IntegerField(null=True)
    situacao = models.CharField(max_length=40)
    pontos = models.IntegerField()

    class Meta:
        ordering = ["id"]


class Contagem(models.Model):
    dia = models.DateField()  # o dia no horário de Brasília
    nome = models.CharField(max_length=40)  # uma das contagens.NOMES
    valor = models.BigIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["dia", "nome"], name="uma_contagem_por_dia_e_nome")]
