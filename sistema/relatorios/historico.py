"""Histórico dos relatórios e contagens do beta, no PostgreSQL (os modelos estão em models.py).

Guarda só o que o relatório mostra: número e título dos anúncios e os números deles. Nada de token e nenhum dado de
comprador. Cada relatório é de uma conta (contas.Conta): sem a conta, não guarda, e quando ela sai o histórico sai
junto. As contagens do beta (ver contagens.py) são só números por dia, sem dizer de qual conta.
"""

from datetime import timedelta

import analise
from contas.models import Conta
from django.db import connection, transaction
from django.db.models import Max

from . import datas
from .models import AnuncioGuardado, Contagem, RelatorioGuardado

DIAS_DE_HISTORICO = 365  # relatórios mais antigos são apagados uma vez por dia (limpezas.py)
MESES_DE_HISTORICO = round(DIAS_DE_HISTORICO / 30.4)  # como as páginas dizem: 365 dias são 12 meses
MAX_NA_LISTA = 100
CAMPOS_ANUNCIO = ("item_id", "titulo", "visitas", "vendas", "situacao", "pontos")


def _resumo(guardado):
    # O banco (jsonb) não guarda a ordem das chaves: volta na ordem de prioridade das situações.
    return {situacao: guardado.resumo.get(situacao, 0) for situacao in analise.ORDEM}


def _cabecalho(guardado):
    return {"id": guardado.id, "criado_em": guardado.criado_em, "dias": guardado.dias, "total": guardado.total,
            "resumo": _resumo(guardado)}


class Historico:
    def __init__(self, agora=datas.agora):
        self._agora = agora

    def salvar(self, ml_user_id, dias, linhas):
        """Guarda o relatório na conta. Devolve o número dele, ou None se a conta não existe mais (foi apagada enquanto
        o relatório rodava): o relatório não traz a conta de volta."""
        resumo = {situacao: sum(1 for l in linhas if l["situacao"] == situacao) for situacao in analise.ORDEM}
        with transaction.atomic():
            # A linha da conta fica travada até o fim: quem apaga a conta espera, e apaga este relatório junto.
            conta = Conta.objects.select_for_update().filter(ml_user_id=int(ml_user_id)).first()
            if conta is None:
                return None
            guardado = RelatorioGuardado.objects.create(
                conta=conta, criado_em=self._agora().replace(microsecond=0), dias=dias, total=len(linhas),
                resumo=resumo)
            AnuncioGuardado.objects.bulk_create(
                AnuncioGuardado(relatorio=guardado, item_id=l["id"], titulo=l["titulo"], visitas=l["visitas"],
                                vendas=l["vendas"], situacao=l["situacao"], pontos=l["pontos"]) for l in linhas)
        return guardado.id

    def listar(self, ml_user_id):
        guardados = (RelatorioGuardado.objects.filter(conta__ml_user_id=int(ml_user_id))
                     .order_by("-id")[:MAX_NA_LISTA])
        return [_cabecalho(g) for g in guardados]

    def ver(self, ml_user_id, relatorio_id):
        """Um relatório guardado, só se for da conta pedida. Devolve None se não for."""
        guardado = RelatorioGuardado.objects.filter(id=int(relatorio_id), conta__ml_user_id=int(ml_user_id)).first()
        if guardado is None:
            return None
        anuncios = guardado.anuncios.order_by("id").values_list(*CAMPOS_ANUNCIO)
        return {**_cabecalho(guardado),
                "anuncios": [dict(zip(("id",) + CAMPOS_ANUNCIO[1:], a)) for a in anuncios]}

    def id_do_anterior(self, ml_user_id, relatorio_id):
        """O relatório guardado logo antes deste, da mesma conta e do mesmo período: é com ele que se compara.

        Devolve o número dele, ou None se não houver (ou se o relatório pedido não for da conta).
        """
        este = RelatorioGuardado.objects.filter(id=int(relatorio_id), conta__ml_user_id=int(ml_user_id)).first()
        if este is None:
            return None
        return (RelatorioGuardado.objects.filter(conta_id=este.conta_id, dias=este.dias, id__lt=este.id)
                .order_by("-id").values_list("id", flat=True).first())

    def apagar(self, ml_user_id):
        """Apaga todos os relatórios da conta (a conta fica). Devolve quantos foram apagados."""
        _, apagados = RelatorioGuardado.objects.filter(conta__ml_user_id=int(ml_user_id)).delete()
        return apagados.get(RelatorioGuardado._meta.label, 0)

    def apagar_antigos(self, dias):
        """Apaga os relatórios e os dias de contagem do beta com mais de `dias` dias. Devolve quantos relatórios."""
        limite = self._agora() - timedelta(days=dias)
        with transaction.atomic():
            _, apagados = RelatorioGuardado.objects.filter(criado_em__lt=limite).delete()
            # Dia de Brasília. Sai também o dia em que o limite cai: ele já tem contagens mais velhas que o limite.
            Contagem.objects.filter(dia__lte=datas.hoje(limite)).delete()
        return apagados.get(RelatorioGuardado._meta.label, 0)

    # ------------------------------------------------------------ contagens do beta (ver contagens.py)

    def somar_contagens(self, dia, valores):
        """Soma às contagens do dia ({"logins": 1}, por exemplo), de uma vez no banco: dois pedidos ao mesmo tempo
        não perdem nenhuma conta. Só números: nada de conta."""
        tabela = connection.ops.quote_name(Contagem._meta.db_table)
        with connection.cursor() as cursor:
            cursor.executemany(
                f"INSERT INTO {tabela} (dia, nome, valor) VALUES (%s, %s, %s) "
                f"ON CONFLICT (dia, nome) DO UPDATE SET valor = {tabela}.valor + EXCLUDED.valor",
                [(dia, nome, int(valor)) for nome, valor in valores.items()])

    def ler_contagens(self):
        """{dia: {nome: valor}} de todos os dias que têm alguma contagem."""
        dias = {}
        for dia, nome, valor in Contagem.objects.values_list("dia", "nome", "valor"):
            dias.setdefault(dia, {})[nome] = valor
        return dias

    def ultimo_total_de_cada_conta(self):
        """Quantos anúncios tem o último relatório guardado de cada conta, do menor para o maior, sem dizer a conta."""
        ultimos = RelatorioGuardado.objects.values("conta").annotate(ultimo=Max("id")).values("ultimo")
        return sorted(RelatorioGuardado.objects.filter(id__in=ultimos).values_list("total", flat=True))


HISTORICO = Historico()
