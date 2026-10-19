"""Contagens do beta: o que o sistema conta e a página /contagens, que só abre para as contas de ORZY_CONTAS_ADMIN."""

from unittest import mock

from django.db import DatabaseError
from relatorios import contagens, geracao
from relatorios.geracao import ERRO, PRONTO
from relatorios.historico import HISTORICO

from .base import CONTA, LINHA, SistemaBase, com_configuracao, criar_conta


class ContagensSiteTests(SistemaBase):
    def contados(self):
        """As contagens somadas de todos os dias: um teste que passa da meia-noite dá o mesmo total."""
        dias = HISTORICO.ler_contagens()
        return {nome: sum(d.get(nome, 0) for d in dias.values()) for nome in contagens.NOMES}

    def test_conta_logins_relatorios_sem_erro_e_com_erro(self):
        self.entrar()
        self.esperar(self.gerar())  # a conta ainda não tem anúncios: pronto, sem erro
        self.semear()
        self.esperar(self.gerar())
        self.assertEqual(self.contados(), {"logins": 1, "relatorios_prontos": 2, "erros_mercado_livre": 0,
                                           "erros_inesperados": 0, "anuncios_lidos": 2})
        self.ml.erros_por_rota["/users/"] = 403  # o Mercado Livre recusou: conta como erro do Mercado Livre
        self.assertEqual(self.esperar(self.gerar()).estado, ERRO)
        del self.ml.erros_por_rota["/users/"]
        with mock.patch.object(geracao.meus_anuncios, "coletar", side_effect=RuntimeError("falha")), \
                self.assertLogs(level="ERROR"):
            self.assertEqual(self.esperar(self.gerar()).estado, ERRO)
        self.assertEqual(self.contados(), {"logins": 1, "relatorios_prontos": 2, "erros_mercado_livre": 1,
                                           "erros_inesperados": 1, "anuncios_lidos": 2})
        for dia in HISTORICO.ler_contagens().values():
            self.assertLessEqual(set(dia), set(contagens.NOMES), "só os números da lista, nada de conta")

    def test_contagem_que_falha_nao_atrapalha_login_nem_relatorio(self):
        self.semear()
        with mock.patch.object(HISTORICO, "somar_contagens", side_effect=DatabaseError("database is locked")), \
                self.assertLogs(level="ERROR") as registro:
            self.entrar()  # o login termina e leva ao relatório
            relatorio = self.esperar(self.gerar())
        self.assertEqual(relatorio.estado, PRONTO)
        self.assertEqual(len(HISTORICO.listar(CONTA)), 1, "o relatório foi guardado")
        self.assertEqual(sum("contagem do beta" in linha for linha in registro.output), 2)

    def test_pagina_so_para_as_contas_de_orzy_contas_admin(self):
        self.semear()
        self.assertEqual(self.abrir("/contagens").status_code, 404, "sem login")
        self.entrar()
        self.esperar(self.gerar())
        self.assertEqual(self.abrir("/contagens").status_code, 404, "conta fora de ORZY_CONTAS_ADMIN")

        # Mais duas contas no histórico: uma com 1 anúncio e outra com 6, o limite desta configuração.
        for numero, linhas in ((987654321, [LINHA]), (555666777, [LINHA] * 6)):
            criar_conta(numero)
            HISTORICO.salvar(numero, 30, linhas)
        with com_configuracao(contas_admin=frozenset({CONTA}), max_anuncios=6):
            self.entrar()
            resposta = self.abrir("/contagens")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Cache-Control"], "no-store")
        texto = self.texto(resposta)
        self.assertIn('<li><span>Contas com relatório guardado</span><b class="num">3</b></li>', texto)
        self.assertIn('<li><span>Anúncios por conta: menor, média e maior</span><b class="num">1 · 3 · 6</b></li>',
                      texto)
        self.assertIn('<li><span>Contas no limite de 6 anúncios por relatório</span><b class="num">1</b></li>', texto)
        self.assertIn('<li><span>Logins</span><b class="num">2</b></li>', texto)
        self.assertIn('<li><span>Relatórios sem erro</span><b class="num">1 de 1 (100%)</b></li>', texto)
        self.assertIn('<li><span>Anúncios lidos</span><b class="num">2</b></li>', texto)
        self.assertIn('<th scope="col">Dia</th><th scope="col" class="n">Logins</th>', texto)
        for dia, valores in HISTORICO.ler_contagens().items():
            celulas = "".join(f'<td class="n">{valores.get(nome, 0)}</td>' for nome in contagens.NOMES)
            self.assertIn(f"<tr><td>{dia:%d/%m/%Y}</td>{celulas}</tr>", texto)
        for privado in ("111222333", "987654321", "555666777", "Caixa de som", "MLB1000000002", "MLB9",
                        "outra conta"):
            self.assertNotIn(privado, texto)
        self.assertNotIn('href="/contagens"', self.texto(self.abrir("/relatorio")), "nenhum link leva à página")

    def test_pagina_sem_nada_contado(self):
        self.entrar_sem_mercado_livre({"id": CONTA, "apelido": "LOJA_TESTE"})
        with com_configuracao(contas_admin=frozenset({CONTA})):
            texto = self.texto(self.abrir("/contagens"))
        self.assertIn('<li><span>Contas com relatório guardado</span><b class="num">0</b></li>', texto)
        self.assertIn("Ainda não há relatório guardado.", texto)
        self.assertIn("Nada contado ainda.", texto)
