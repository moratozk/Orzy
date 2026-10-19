"""As páginas do histórico: a linha do tempo, um relatório guardado, o que mudou desde o anterior e apagar tudo."""

import re

from relatorios.geracao import PRONTO
from relatorios.historico import HISTORICO

from .base import CONTA, LINHA, TITULO_BOM, SistemaBase


class HistoricoSiteTests(SistemaBase):
    def guardados(self):
        return [r["id"] for r in HISTORICO.listar(CONTA)]

    def test_historico_vazio(self):
        self.entrar()
        resposta = self.abrir("/historico")
        self.assertEqual(resposta.status_code, 200)
        texto = self.texto(resposta)
        self.assertIn("Você ainda não tem relatórios guardados", texto)
        self.assertNotIn("Apagar meu histórico", texto, "nada para apagar")

    def test_abre_no_relatorio_mais_recente(self):
        self.semear()
        self.entrar()
        self.esperar(self.gerar())
        self.esperar(self.gerar(dias=60))
        ultimo, primeiro = self.guardados()
        texto = self.texto(self.abrir("/historico"))
        self.assertIn("2 relatórios guardados.", texto)
        self.assertIn("não é atualizado depois", texto)
        self.assertIn("últimos 60 dias", texto)
        self.assertRegex(texto, rf'href="/historico/{ultimo}" aria-label="[^"]*" aria-current="true"')
        self.assertRegex(texto, rf'href="/historico/{primeiro}" aria-label="[^"]*">')
        self.assertIn("Mais recente", texto)
        # Abrir o primeiro marca o cartão dele.
        texto = self.texto(self.abrir(f"/historico/{primeiro}"))
        self.assertRegex(texto, rf'href="/historico/{primeiro}" aria-label="[^"]*" aria-current="true"')
        self.assertIn("últimos 30 dias", texto)

    def test_outra_conta_nao_ve_o_relatorio_guardado(self):
        de_outra_conta = HISTORICO.salvar(999, 30, [LINHA])
        self.entrar()
        self.assertEqual(self.abrir(f"/historico/{de_outra_conta}").status_code, 404)
        self.assertEqual(self.abrir("/historico/99999999").status_code, 404)

    def test_apagar_pede_confirmacao(self):
        self.semear()
        self.entrar()
        self.esperar(self.gerar())
        self.assertIn("Apagar meu histórico", self.texto(self.abrir("/historico")))

        resposta = self.enviar("/historico/apagar")
        self.assertEqual(resposta.status_code, 400, "apagar sem confirmar não pode")
        self.assertIn("Confirme que quer apagar o histórico.", self.texto(resposta))
        self.assertEqual(len(self.guardados()), 1)

        resposta = self.enviar("/historico/apagar", {"confirmo": "on"})
        self.assertEqual((resposta.status_code, resposta["Location"]), (303, "/historico"))
        self.assertEqual(self.guardados(), [])
        self.assertFalse(any(r.estado == PRONTO for r in self.sessao()["relatorios"].values()),
                         "os relatórios prontos também saem da sessão")

    def test_busca_e_filtro_no_relatorio_guardado(self):
        self.semear()
        self.entrar()
        self.esperar(self.gerar())
        guardado = self.guardados()[0]
        pagina = self.texto(self.abrir(f"/historico/{guardado}?busca=caixa&situacao=XYZ"))
        texto = pagina.split('id="todos"', 1)[1]
        self.assertIn(f'action="/historico/{guardado}#todos"', texto)
        self.assertIn("Caixa de som", texto)
        self.assertNotIn("Fone de Ouvido", texto)
        self.assertIn("Mostrando 1 de 2 anúncios.", texto, "situação desconhecida não filtra")
        self.assertIn(f'<a href="/historico/{guardado}#todos">Ver todos</a>', texto)

    def test_compara_com_o_relatorio_anterior_do_mesmo_periodo(self):
        self.semear()
        self.ml.adicionar_item("MLB1000000003", "Capa <b>antiga</b> para celular", visitas=50)
        self.entrar()
        primeiro = self.esperar(self.gerar()).id
        self.assertNotIn("#mudancas", self.texto(self.abrir(f"/relatorio/{primeiro}")),
                         "sem relatório anterior, não há o que comparar")
        guardado_1 = self.guardados()[0]
        texto = self.texto(self.abrir(f"/historico/{guardado_1}"))
        self.assertIn("Ainda não há um relatório anterior de 30 dias para comparar", texto)

        # Entre um relatório e outro, o vendedor mudou o título do fone, que passou a ter visitas e vendas;
        # a capa saiu dos anúncios ativos e entrou um suporte.
        self.ml.itens["MLB1000000001"]["title"] = "Fone Bluetooth <script>x</script> Novo"
        self.ml.visitas["MLB1000000001"] = 200
        self.ml.adicionar_pedido("MLB1000000001", quantidade=5, dias_atras=1)
        self.ml.itens["MLB1000000003"]["status"] = "paused"
        self.ml.adicionar_item("MLB1000000004", "Suporte de mesa", visitas=10)
        self.esperar(self.gerar(dias=60))  # outro período: fica fora da comparação
        segundo = self.esperar(self.gerar()).id
        guardado_2 = self.guardados()[0]

        self.assertIn(f'href="/historico/{guardado_2}#mudancas"', self.texto(self.abrir(f"/relatorio/{segundo}")))

        texto = self.texto(self.abrir(f"/historico/{guardado_2}"))
        self.assertIn('id="mudancas"', texto)
        self.assertIn(f'<a class="hi-ir" href="/historico/{guardado_1}">', texto,
                      "compara com o de 30, não com o de 60")
        self.assertIn("Mostra o que mudou, não o porquê", texto)
        for nome in ("Mudaram de situação", "Novos neste relatório", "Não estão mais no relatório",
                     "Títulos que mudaram"):
            self.assertIn(f'<li><b class="num">1</b><span>{nome}</span></li>', texto)
        # Visitas: 0 + 120 + 50 antes, 200 + 120 + 10 agora. Vendas: 2 antes, 7 agora.
        self.assertIn('<span class="num hi-antes">170</span>', texto)
        self.assertIn('<b class="num">330</b><em class="sobe">+160</em>', texto)
        self.assertIn('<b class="num">7</b><em class="sobe">+5</em>', texto)
        self.assertRegex(texto, r'<span class="chip">Pouca visita</span></span><svg class="ico hi-seta"[^>]*>.*?'
                                r'<span class="so-leitor">para</span><span class="sit s-vb"><span class="chip">'
                                r'Vendendo bem</span>')
        self.assertIn(f"<small>Título antes: {TITULO_BOM}</small>", texto)
        self.assertIn('<em class="sobe">+200</em><b class="num">200</b>', texto)
        self.assertIn("Fone Bluetooth &lt;script&gt;x&lt;/script&gt; Novo", texto)
        self.assertNotIn("<script>x", texto)
        self.assertIn('<li class="saiu"><b title="Capa &lt;b&gt;antiga&lt;/b&gt; para celular">'
                      'Capa &lt;b&gt;antiga&lt;/b&gt; para celular</b></li>', texto)
        self.assertIn('<b title="Suporte de mesa">Suporte de mesa</b><small class="novo">Novo neste relatório</small>',
                      texto)
        self.assertEqual(len(re.findall(r'aria-current="true"', texto)), 1)
