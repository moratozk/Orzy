"""O histórico no PostgreSQL (o que fica guardado e por quanto tempo) e as limpezas em segundo plano."""

import threading
from datetime import date, datetime, timedelta, timezone

import analise
from django.db import connections
from django.test import SimpleTestCase, TestCase, TransactionTestCase
from relatorios import limpezas
from relatorios.historico import Historico
from relatorios.models import AnuncioGuardado, Contagem, RelatorioGuardado


class HistoricoTests(TestCase):
    def setUp(self):
        self.relogio = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
        self.historico = Historico(agora=lambda: self.relogio)
        self.linhas = [
            {"id": "MLB1", "titulo": "Anúncio A", "visitas": 5, "vendas": 0, "situacao": "VISITA SEM VENDA",
             "pontos": 3},
            {"id": "MLB2", "titulo": "Anúncio B", "visitas": None, "vendas": None, "situacao": "POUCA VISITA",
             "pontos": 0},
        ]

    def salvar(self, conta, dias, minutos_depois=1):
        self.relogio += timedelta(minutes=minutos_depois)
        return self.historico.salvar(conta, dias, self.linhas)

    def test_guarda_so_o_que_a_politica_de_privacidade_diz(self):
        # Seção 6 da Política: um campo novo aqui precisa entrar no texto antes.
        def campos(modelo):
            return {campo.name for campo in modelo._meta.get_fields()}
        self.assertEqual(campos(RelatorioGuardado), {"id", "ml_user_id", "criado_em", "dias", "total", "resumo",
                                                     "anuncios"})
        self.assertEqual(campos(AnuncioGuardado), {"id", "relatorio", "item_id", "titulo", "visitas", "vendas",
                                                   "situacao", "pontos"})
        self.assertEqual(campos(Contagem), {"id", "dia", "nome", "valor"}, "só números por dia, sem a conta")

    def test_salva_lista_ve_e_apaga_so_da_conta_pedida(self):
        id_ = self.salvar(111, 30)
        self.salvar(222, 30)
        lista = self.historico.listar(111)
        self.assertEqual([r["id"] for r in lista], [id_])
        self.assertEqual((lista[0]["criado_em"], lista[0]["dias"], lista[0]["total"]),
                         (datetime(2026, 10, 15, 12, 1, tzinfo=timezone.utc), 30, 2))
        self.assertEqual(list(lista[0]["resumo"]), analise.ORDEM, "as situações na ordem de prioridade")
        self.assertEqual(lista[0]["resumo"]["VISITA SEM VENDA"], 1)
        dados = self.historico.ver(111, id_)
        self.assertEqual(dados["anuncios"], self.linhas, "volta igual, com acento e números vazios")
        self.assertIsNone(self.historico.ver(222, id_), "outra conta não pode ver o relatório")
        self.assertIsNone(self.historico.ver(111, id_ + 999_999), "relatório que não existe")
        self.assertEqual(self.historico.apagar(111), 1)
        self.assertEqual(self.historico.listar(111), [])
        self.assertFalse(AnuncioGuardado.objects.filter(relatorio__ml_user_id=111).exists(), "os anúncios saem junto")
        self.assertEqual(len(self.historico.listar(222)), 1)

    def test_lista_do_mais_novo_para_o_mais_velho(self):
        ids = [self.salvar(111, 30) for _ in range(3)]
        self.assertEqual([r["id"] for r in self.historico.listar(111)], ids[::-1])

    def test_apaga_relatorios_mais_velhos_que_o_prazo(self):
        self.salvar(111, 30)
        self.salvar(111, 30, minutos_depois=366 * 24 * 60)  # um ano e um dia depois
        self.assertEqual(self.historico.apagar_antigos(365), 1)
        self.assertEqual(len(self.historico.listar(111)), 1)

    def test_anterior_e_o_ultimo_da_mesma_conta_e_do_mesmo_periodo(self):
        primeiro = self.salvar(111, 30)
        self.salvar(111, 60)  # outro período: os números não são comparáveis
        self.salvar(222, 30)  # outra conta: nunca
        segundo = self.salvar(111, 30)
        terceiro = self.salvar(111, 30)
        self.assertIsNone(self.historico.id_do_anterior(111, primeiro))
        self.assertEqual(self.historico.id_do_anterior(111, segundo), primeiro)
        self.assertEqual(self.historico.id_do_anterior(111, terceiro), segundo)
        self.assertIsNone(self.historico.id_do_anterior(222, terceiro), "o relatório pedido não é da conta 222")

    def test_contagens_somam_por_dia(self):
        self.assertEqual(self.historico.ler_contagens(), {})
        self.historico.somar_contagens(date(2026, 10, 15), {"logins": 1})
        self.historico.somar_contagens(date(2026, 10, 15), {"logins": 2, "relatorios_prontos": 1})
        self.historico.somar_contagens(date(2026, 10, 16), {"anuncios_lidos": 40})
        self.assertEqual(self.historico.ler_contagens(), {date(2026, 10, 15): {"logins": 3, "relatorios_prontos": 1},
                                                          date(2026, 10, 16): {"anuncios_lidos": 40}})

    def test_apaga_contagens_mais_velhas_que_o_prazo_pelo_dia_de_brasilia(self):
        for dia in (date(2025, 10, 13), date(2025, 10, 14), date(2025, 10, 15), date(2026, 10, 14)):
            self.historico.somar_contagens(dia, {"logins": 1})
        # 01h00 em UTC ainda é 14/10 em Brasília: o limite de 365 dias cai em 14/10/2025, às 22h00 de Brasília.
        # O dia 14/10/2025 já tem contagens mais velhas que o limite e sai inteiro; o 15/10/2025 fica.
        self.relogio = datetime(2026, 10, 15, 1, 0, tzinfo=timezone.utc)
        self.historico.apagar_antigos(365)
        self.assertEqual(self.historico.ler_contagens(), {date(2025, 10, 15): {"logins": 1},
                                                          date(2026, 10, 14): {"logins": 1}})

    def test_anuncios_do_ultimo_relatorio_de_cada_conta(self):
        self.assertEqual(self.historico.ultimo_total_de_cada_conta(), [])
        self.salvar(111, 30)  # 2 anúncios
        self.relogio += timedelta(minutes=1)
        self.historico.salvar(111, 60, self.linhas[:1])  # o último da conta 111 tem 1
        self.salvar(222, 30)
        self.assertEqual(self.historico.ultimo_total_de_cada_conta(), [1, 2], "um número por conta, sem a conta")


class ContagensAoMesmoTempoTests(TransactionTestCase):
    def test_pedidos_ao_mesmo_tempo_nao_perdem_contagem(self):
        historico = Historico()

        def somar():
            try:
                for _ in range(25):
                    historico.somar_contagens(date(2026, 10, 15), {"logins": 1})
            finally:
                connections.close_all()

        threads = [threading.Thread(target=somar) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        self.assertEqual(historico.ler_contagens(), {date(2026, 10, 15): {"logins": 100}})


class LimpezasTests(SimpleTestCase):
    def test_apaga_o_historico_antigo_todo_dia_e_segue_depois_de_um_erro(self):
        parar = threading.Event()
        chamadas = []

        class HistoricoFalso:
            def apagar_antigos(self, dias):
                chamadas.append(dias)
                if len(chamadas) == 1:
                    raise RuntimeError("banco fora do ar")
                if len(chamadas) == 3:
                    parar.set()
                return 0

        with self.assertLogs(level="ERROR"):
            limpezas.apagar_antigos_todo_dia(HistoricoFalso(), parar, intervalo=0.01)
        self.assertEqual(chamadas, [365, 365, 365], "um erro não pode parar a limpeza dos dias seguintes")

    def test_apaga_as_sessoes_vencidas_a_cada_intervalo_e_segue_depois_de_um_erro(self):
        parar = threading.Event()
        chamadas = []

        class SessoesFalsas:
            def limpar(self, antecedencia):
                chamadas.append(antecedencia)
                if len(chamadas) == 1:
                    raise RuntimeError("falha qualquer")
                if len(chamadas) == 3:
                    parar.set()

        with self.assertLogs(level="ERROR"):
            limpezas.apagar_sessoes_vencidas_sempre(SessoesFalsas(), parar, intervalo=0.01)
        self.assertEqual(chamadas, [0.01, 0.01, 0.01], "apaga um intervalo antes do prazo, e um erro não para")

    def test_liga_as_duas_limpezas(self):
        parar = threading.Event()
        self.addCleanup(parar.set)
        historico_limpo, sessoes_limpas = threading.Event(), threading.Event()

        class HistoricoFalso:
            def apagar_antigos(self, dias):
                historico_limpo.set()
                return 0

        class SessoesFalsas:
            def limpar(self, antecedencia):
                sessoes_limpas.set()

        limpezas.ligar(parar, historico=HistoricoFalso(), sessoes=SessoesFalsas())
        self.assertTrue(historico_limpo.wait(5), "a limpeza do histórico não ligou")
        self.assertTrue(sessoes_limpas.wait(5), "a limpeza das sessões não ligou")
