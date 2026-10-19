"""O relatório: gerar, acompanhar o andamento, ver o resultado, filtrar e baixar a planilha."""

import re
from datetime import datetime, timezone
from unittest import mock

from relatorios.geracao import ERRO, PASSOS, PRONTO, Relatorio
from relatorios.historico import HISTORICO

from .base import CONTA, Navegador, SistemaBase, com_configuracao


class RelatorioTests(SistemaBase):
    def test_gera_mostra_resultado_com_escape_e_baixa_csv(self):
        self.semear()
        self.entrar()
        relatorio_id = self.gerar()
        relatorio = self.esperar(relatorio_id)
        self.assertEqual(relatorio.estado, PRONTO)

        resposta = self.abrir(f"/relatorio/{relatorio_id}")
        self.assertEqual(resposta.status_code, 200)
        texto = self.texto(resposta)
        self.assertIn("Comece por estes", texto)
        self.assertIn("Caixa de som", texto)
        self.assertNotIn("<script>alert(1)</script>", texto, "título do Mercado Livre tem que sair escapado")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; Caixa de som", texto)
        self.assertIn("Olá, LOJA_TESTE!", texto)
        # Os termos do Mercado Livre (5.3) pedem que o aplicativo diga quando os dados foram atualizados.
        self.assertRegex(texto, r"Dados buscados no Mercado Livre em \d{2}/\d{2}/\d{4} às \d{2}:\d{2}")
        # A hora é a de Brasília: 02h30 em UTC ainda é o dia anterior aqui.
        relatorio.gerado_em = datetime(2026, 10, 15, 2, 30, tzinfo=timezone.utc)
        texto = self.texto(self.abrir(f"/relatorio/{relatorio_id}"))
        self.assertIn("Dados buscados no Mercado Livre em 14/10/2026 às 23:30 (horário de Brasília)", texto)

        resposta = self.abrir(f"/relatorio/{relatorio_id}/csv")
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.content.startswith("﻿".encode("utf-8")), "o CSV precisa do BOM para o Excel")
        csv_texto = resposta.content.decode("utf-8-sig")
        self.assertTrue(csv_texto.splitlines()[0].startswith("id;titulo;preco;estoque;visitas_30d;vendas_30d"))
        self.assertIn("MLB1000000002", csv_texto)
        self.assertEqual(resposta["Content-Type"], "text/csv; charset=utf-8")
        self.assertEqual(resposta["Content-Disposition"], 'attachment; filename="orzy-anuncios-30-dias.csv"')

        guardado = HISTORICO.listar(CONTA)
        self.assertEqual(len(guardado), 1)
        self.assertEqual(guardado[0]["total"], 2)

    def test_numeros_do_alto_e_o_que_olhar_primeiro(self):
        self.semear()
        self.entrar()
        texto = self.texto(self.abrir(f"/relatorio/{self.esperar(self.gerar()).id}"))
        # 120 visitas e 2 vendas no total: 1,67%, acima do limite de 1%.
        self.assertIn('<span class="num">120</span> <small>em 30 dias</small>', texto)
        self.assertIn('<span class="num">1,67%</span>', texto)
        self.assertIn("acima de 1%", texto)
        # O fone (0 visitas) está em "Pouca visita": o bloco leva ao filtro da lista.
        self.assertIn('<a href="?situacao=POUCA%20VISITA#todos">', texto)
        self.assertIn("<b>1 anúncio</b>", texto)

    def test_formulario_mostra_os_relatorios_prontos_da_sessao(self):
        self.semear()
        self.entrar()
        texto = self.texto(self.abrir("/relatorio"))
        self.assertIn("Olá, LOJA_TESTE!", texto)
        self.assertNotIn("Gerados desde que você entrou", texto)
        relatorio_id = self.esperar(self.gerar()).id
        texto = self.texto(self.abrir("/relatorio"))
        self.assertIn("Gerados desde que você entrou", texto)
        self.assertIn(f'<a href="/relatorio/{relatorio_id}"><b>30 dias</b>', texto)
        self.assertIn(" · 2 anúncios</span>", texto)

    def test_periodo_fora_das_opcoes_vale_30_dias(self):
        self.semear()
        self.entrar()
        for dias in (7, "abc"):
            self.assertEqual(self.esperar(self.gerar(dias)).dias, 30)

    def test_busca_e_filtro_na_tabela_de_todos_os_anuncios(self):
        self.semear()
        self.entrar()
        relatorio_id = self.esperar(self.gerar()).id

        def todos(consulta):
            pagina = self.texto(self.abrir(f"/relatorio/{relatorio_id}?{consulta}"))
            return pagina.split('id="todos"', 1)[1]  # só a lista de todos, sem "Comece por estes"

        texto = todos("")
        self.assertIn(f'action="/relatorio/{relatorio_id}#todos"', texto)
        self.assertIn("Fone de Ouvido", texto)
        self.assertIn("Caixa de som", texto)
        self.assertNotIn("Mostrando", texto)

        texto = todos("busca=FONE+bluetooth")
        self.assertIn("Fone de Ouvido", texto)
        self.assertNotIn("Caixa de som", texto)
        self.assertIn("Mostrando 1 de 2 anúncios.", texto)
        self.assertIn('value="FONE bluetooth"', texto)
        self.assertIn(f'<a href="/relatorio/{relatorio_id}#todos">Ver todos</a>', texto)

        texto = todos("situacao=POUCA+VISITA")
        self.assertIn('<option value="POUCA VISITA" selected>Pouca visita (1)</option>', texto)
        self.assertIn("Fone de Ouvido", texto)
        self.assertNotIn("Caixa de som", texto)

        self.assertIn("Nenhum anúncio com essa busca.", todos("busca=geladeira"))
        texto = todos("busca=%3Cscript%3E%22")
        self.assertIn('value="&lt;script&gt;&quot;"', texto, "o que a pessoa digitou volta escapado")
        self.assertNotIn("<script>", texto)

    def test_o_relatorio_passa_por_todas_as_etapas_da_pagina_de_andamento(self):
        # Se meus_anuncios.coletar() ganhar uma etapa, ela precisa entrar em PASSOS (geracao.py).
        self.semear()
        self.entrar()
        with mock.patch.object(Relatorio, "andar", autospec=True, side_effect=Relatorio.andar) as andar:
            relatorio = self.esperar(self.gerar())
        self.assertEqual(andar.call_count, len(PASSOS))
        dados = self.abrir(f"/relatorio/{relatorio.id}/andamento.json").json()
        self.assertEqual((dados["estado"], dados["pct"], dados["passo"]), ("pronto", 100, len(PASSOS)))
        self.assertEqual([e["nome"] for e in dados["etapas"]], [nome for nome, _ in PASSOS])

    def test_um_relatorio_por_vez_em_cada_sessao(self):
        self.entrar()
        parado = Relatorio(CONTA, 30)  # ainda rodando
        self.sessao()["relatorios"][parado.id] = parado
        resposta = self.enviar("/relatorio/gerar", {"dias": 30})
        self.assertEqual(resposta.status_code, 200)
        texto = self.texto(resposta)
        self.assertIn("Já tem um relatório sendo gerado", texto)
        self.assertIn(f'<a href="/relatorio/{parado.id}">Ver andamento</a>', texto)
        self.assertIn("Gerando seu relatório", self.texto(self.abrir(f"/relatorio/{parado.id}")))
        self.assertEqual(self.abrir(f"/relatorio/{parado.id}/csv").status_code, 404, "ainda não tem planilha")

        # O andamento: duas etapas começadas e metade da segunda feita.
        parado.andar("Buscando anúncios ativos...")
        parado.andar("10 anúncios encontrados. Buscando detalhes...")
        parado.progredir(5, 10)
        dados = self.abrir(f"/relatorio/{parado.id}/andamento.json").json()
        self.assertEqual((dados["estado"], dados["pct"], dados["passo"]), ("gerando", 12, 2))
        self.assertEqual(dados["etapas"][0], {"nome": "Anúncios ativos", "estado": "feita", "conta": "pronto"})
        self.assertEqual(dados["etapas"][1], {"nome": "Detalhes dos anúncios", "estado": "ativa", "conta": "5 de 10",
                                              "barra": 50})
        self.assertEqual(dados["etapas"][2]["conta"], "na fila")
        pagina = self.texto(self.abrir(f"/relatorio/{parado.id}"))
        self.assertIn('data-pct="12"', pagina)
        self.assertIn('<noscript><meta http-equiv="refresh" content="10"></noscript>', pagina, "funciona sem JS")

    def test_pedido_de_outro_site_e_recusado(self):
        self.entrar()
        for resposta in (self.enviar("/relatorio/gerar", {"dias": 30}, origem="https://site-estranho.example"),
                         self.enviar("/relatorio/gerar", {"dias": 30}, com_codigo=False)):
            self.assertEqual(resposta.status_code, 403)
            self.assertIn("Pedido recusado", self.texto(resposta))
        self.assertEqual(self.sessao()["relatorios"], {})

    def test_outra_sessao_nao_ve_o_relatorio_de_quem_gerou(self):
        self.semear()
        self.entrar()
        relatorio_id = self.esperar(self.gerar()).id
        outra = self.entrar_sem_mercado_livre({"id": 999, "apelido": "OUTRA"}, Navegador())
        for caminho in ("", "/csv", "/andamento.json"):
            self.assertEqual(self.abrir(f"/relatorio/{relatorio_id}{caminho}", outra).status_code, 404, caminho)

    def test_token_vencido_pede_novo_login_sem_renovar_sozinho(self):
        self.semear()
        self.entrar()
        self.ml.revogar_access_tokens()
        antes = len(self.chamadas_de_token())
        relatorio = self.esperar(self.gerar())
        self.assertEqual(relatorio.estado, ERRO)
        self.assertIn("venceu", relatorio.mensagem)
        self.assertEqual(len(self.chamadas_de_token()), antes, "o site não pode renovar com refresh token")
        texto = self.texto(self.abrir(f"/relatorio/{relatorio.id}"))
        self.assertIn("Não deu para gerar o relatório", texto)
        self.assertIn("Tentar de novo", texto)

    def test_conta_sem_anuncios_avisa_sem_erro(self):
        self.entrar()
        relatorio = self.esperar(self.gerar())
        self.assertEqual((relatorio.estado, relatorio.mensagem), (PRONTO, "Nenhum anúncio ativo nessa conta."))
        resposta = self.abrir(f"/relatorio/{relatorio.id}")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Nenhum anúncio ativo nessa conta.", self.texto(resposta))
        self.assertEqual(HISTORICO.listar(CONTA), [], "relatório vazio não vai para o histórico")

    def test_avisa_quando_chega_no_limite_de_anuncios(self):
        self.semear()
        self.entrar()
        with com_configuracao(max_anuncios=2):
            relatorio = self.esperar(self.gerar())
        self.assertIn("Esta versão lê até 2 anúncios por relatório.", relatorio.aviso)
        self.assertIn("Esta versão lê até 2 anúncios por relatório.",
                      self.texto(self.abrir(f"/relatorio/{relatorio.id}")))

    def test_endereco_errado_ou_metodo_errado(self):
        self.entrar()
        self.assertEqual(self.abrir("/relatorio/nao-existe").status_code, 404)
        self.assertEqual(self.abrir("/relatorio/gerar").status_code, 404, "gerar só com o formulário")
        resposta = self.client.head("/relatorio", secure=True)
        self.assertEqual((resposta.status_code, resposta.content), (200, b""))

    def test_paginas_do_sistema_tem_o_rodape_e_o_topo(self):
        self.semear()
        self.entrar()
        relatorio_id = self.esperar(self.gerar()).id
        for caminho in ("/relatorio", f"/relatorio/{relatorio_id}", "/historico"):
            texto = self.texto(self.abrir(caminho))
            rodape = texto[texto.index('<footer class="si-rodape">'):]
            for link in ('href="/privacidade"', 'href="/termos"', 'href="mailto:orzy.suporte@gmail.com"'):
                self.assertIn(link, rodape, caminho)
            self.assertIn('<span class="app-avatar si-avatar" aria-hidden="true" title="Conectado como LOJA_TESTE">LT'
                          '</span>', texto)
            self.assertIsNotNone(re.search(r'<form class="si-sair-form" method="post" action="/sair">'
                                           r'<input type="hidden" name="csrfmiddlewaretoken"', texto), caminho)
