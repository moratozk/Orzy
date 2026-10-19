"""Páginas públicas (início, textos legais, erro, robots.txt), cabeçalhos de segurança e os arquivos de /static/."""

import gzip
import re
import tempfile
from pathlib import Path
from unittest import mock

import analise
from django.test import override_settings

from .base import SistemaBase


class PaginasTests(SistemaBase):
    def test_cabecalhos_de_seguranca(self):
        for caminho in ("/", "/privacidade", "/nao-existe"):
            resposta = self.abrir(caminho)
            politica = resposta["Content-Security-Policy"]
            for regra in ("default-src 'self'", "script-src 'self'", "style-src 'self'", "img-src 'self' data:",
                          "form-action 'self'", "frame-ancestors 'none'", "base-uri 'none'"):
                self.assertIn(regra, politica, caminho)
            self.assertEqual(resposta["Referrer-Policy"], "same-origin", caminho)
            self.assertEqual(resposta["X-Frame-Options"], "DENY", caminho)
            self.assertEqual(resposta["X-Content-Type-Options"], "nosniff", caminho)
            self.assertEqual(resposta["Cache-Control"], "no-store", caminho)

    def test_pedido_com_outro_endereco_e_recusado(self):
        for caminho in ("/", "/saude", "/relatorio"):
            resposta = self.abrir(caminho, HTTP_HOST="orzy.example")
            self.assertEqual(resposta.status_code, 400, caminho)
            self.assertIn("Não entendi esse pedido.", self.texto(resposta), caminho)

    def test_html_sem_estilo_nem_script_dentro_da_pagina(self):
        # A CSP bloqueia style= e <script> sem arquivo: o que vem dos dados vai em data- e o JS aplica.
        self.semear()
        self.entrar()
        relatorio_id = self.esperar(self.gerar()).id
        for caminho in ("/", "/privacidade", "/termos", "/nao-existe", "/relatorio", f"/relatorio/{relatorio_id}",
                        "/historico"):
            texto = self.texto(self.abrir(caminho))
            self.assertNotIn("style=", texto, caminho)
            self.assertNotIn("<style", texto, caminho)
            self.assertIsNone(re.search(r"<script(?![^>]*\bsrc=)", texto), caminho)
            self.assertIsNone(re.search(r"\son[a-z]+=", texto), f"{caminho}: onclick= e parecidos")

    def test_paginas_saem_comprimidas(self):
        resposta = self.abrir("/", HTTP_ACCEPT_ENCODING="gzip")
        self.assertEqual(resposta["Content-Encoding"], "gzip")
        self.assertTrue(gzip.decompress(resposta.content).startswith(b"<!doctype html>"))

    def test_arquivos_estaticos_com_o_resumo_no_nome(self):
        pagina = self.texto(self.abrir("/"))
        for nome, tipo in (("orzy-base.css", "text/css"), ("orzy-inicio.js", "text/javascript"),
                           ("geist.woff2", "font/woff2"), ("favicon.svg", "image/svg+xml")):
            raiz, extensao = nome.rsplit(".", 1)
            achado = re.search(rf'"(/static/{raiz}\.[0-9a-f]{{12}}\.{extensao})"', pagina)
            self.assertIsNotNone(achado, nome)
            resposta = self.abrir(achado.group(1))
            self.assertEqual(resposta.status_code, 200, nome)
            self.assertEqual(resposta["Content-Type"].split(";")[0], tipo, nome)
            self.assertIn("immutable", resposta["Cache-Control"],
                          "o navegador guarda: o nome muda quando o arquivo muda")
        resposta = self.abrir(re.search(r'"(/static/orzy-base\.[0-9a-f]{12}\.css)"', pagina).group(1),
                              HTTP_ACCEPT_ENCODING="gzip")
        self.assertEqual(resposta["Content-Encoding"], "gzip", "CSS e JS saem comprimidos")
        css = self.abrir(re.search(r'"(/static/orzy-fontes\.[0-9a-f]{12}\.css)"', pagina).group(1))
        self.assertRegex(b"".join(css.streaming_content).decode(), r'url\("geist\.[0-9a-f]{12}\.woff2"\)',
                         "o CSS aponta para a fonte com o resumo no nome")
        for errado in ("/static/settings.py", "/static/../orzy/settings.py", "/static/nao-existe.css"):
            self.assertEqual(self.abrir(errado).status_code, 404, errado)

    def test_robots_e_saude(self):
        resposta = self.abrir("/robots.txt")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(resposta["Cache-Control"], "public, max-age=86400")
        for caminho in ("/entrar", "/retorno", "/relatorio", "/historico", "/conta"):
            self.assertIn(f"Disallow: {caminho}\n".encode(), resposta.content)
        self.assertNotIn(b"Disallow: /\n", resposta.content, "a página inicial e os textos legais continuam abertos")
        resposta = self.abrir("/saude")
        self.assertEqual((resposta.status_code, resposta.content), (200, b"ok"))

    def test_pagina_que_nao_existe(self):
        resposta = self.abrir("/nao-existe")
        self.assertEqual(resposta.status_code, 404)
        texto = self.texto(resposta)
        self.assertIn('<p class="sc-rotulo er-codigo">Erro 404</p>', texto)
        self.assertIn("Não encontrei essa página.", texto)
        self.assertIn("orzy.suporte@gmail.com", texto)

    def test_inicio_sem_login_leva_ao_mercado_livre(self):
        resposta = self.abrir("/")
        self.assertEqual(resposta.status_code, 200)
        texto = self.texto(resposta)
        self.assertIn('<meta name="description" content="Conecte sua conta do Mercado Livre', texto)
        self.assertIn('href="/entrar"', texto)
        self.assertNotIn('href="/relatorio"', texto)
        # Junto de cada botão Conectar, o aviso dos Termos de Uso e da Política de Privacidade.
        self.assertEqual(texto.count('href="/entrar"'), texto.count("Ao conectar, você aceita os"))
        self.assertIn('<a href="/termos">Termos de Uso</a>', texto)
        self.assertIn('<a href="/privacidade">Política de Privacidade</a>', texto)
        self.assertIn("Até 300 anúncios", texto)
        self.assertIn("30, 60, 90 ou 150 dias", texto)

    def test_inicio_com_login_leva_ao_relatorio(self):
        self.entrar()
        texto = self.texto(self.abrir("/"))
        self.assertIn('href="/relatorio">Ver meu relatório', texto)
        self.assertIn('href="/relatorio"><span>Meu relatório</span>', texto)
        self.assertNotIn('href="/entrar"', texto)
        self.assertNotIn("Ao conectar", texto)

    def test_inicio_acompanha_os_limites_do_analise(self):
        with mock.patch.object(analise, "POUCAS_VISITAS", 50), mock.patch.object(analise, "CONVERSAO_BAIXA", 0.02):
            texto = self.texto(self.abrir("/"))
        self.assertIn("Menos de 50 visitas e nenhuma venda", texto)
        self.assertIn("menos de 1 venda a cada 50", texto)

    def test_apelido_longo_quebra_em_vez_de_empurrar_a_pagina(self):
        # Apelidos como LOJA_DO_JOAO_OFICIAL empurravam a página para o lado num celular de 360 px.
        css = (Path(__file__).resolve().parent.parent / "publico" / "static" / "orzy-sistema.css").read_text()
        self.assertRegex(css, r"\.pn-saudacao h1 \{[^}]*overflow-wrap: anywhere")


class TextosLegaisTests(SistemaBase):
    def setUp(self):
        super().setUp()
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.pasta_legal = Path(pasta.name)
        trocar = override_settings(ORZY_PASTA_LEGAL=self.pasta_legal)
        trocar.enable()
        self.addCleanup(trocar.disable)

    def test_sem_o_arquivo_a_pagina_avisa(self):
        resposta = self.abrir("/privacidade")
        self.assertEqual(resposta.status_code, 200)
        texto = self.texto(resposta)
        self.assertIn("<title>Política de Privacidade · Orzy</title>", texto)
        self.assertIn("Este texto ainda está sendo preparado.", texto)

    def test_textos_vem_de_docs_legal_com_escape(self):
        (self.pasta_legal / "termos-de-uso.md").write_text(
            "# Termos de Uso do Orzy\n\n"
            "> **Rascunho.** O que falta está no [LEIA-ME](LEIA-ME.md).\n\n"
            "**Versão:** 0.3 (rascunho)\n\n"
            "Texto com <script>alert(1)</script> e o cookie `orzy_sessao`,\n"
            "que continua na linha de baixo.\n\n"
            "## 1. O que é o Orzy\n\n"
            "- um item que segue\n  na linha seguinte;\n"
            "- leia a [Política](politica-de-privacidade.md#8-os-seus-direitos).\n\n"
            "| Dado | Prazo |\n|---|---|\n| Código de renovação | Não é guardado |\n\n"
            "## 2. Contato\n\n"
            "[clique](javascript:alert(1)) ou veja a [ANPD](https://www.gov.br/anpd). [PREENCHER: CNPJ]\n\n"
            "Escreva para [o Orzy](mailto:orzy.suporte@gmail.com).\n\n"
            "## 2. Contato\n",
            encoding="utf-8")
        resposta = self.abrir("/termos")
        self.assertEqual(resposta.status_code, 200)
        texto = self.texto(resposta)
        self.assertIn("<title>Termos de Uso · Orzy</title>", texto)
        self.assertIn('<h1 class="lg-titulo">Termos de Uso do Orzy</h1>', texto)
        self.assertIn("<blockquote><p><strong>Rascunho.</strong> O que falta está no LEIA-ME.</p></blockquote>", texto)
        self.assertIn("<dd>0.3 (rascunho)</dd>", texto)
        self.assertIn("<dd>Cerca de 1 minuto</dd>", texto)
        self.assertIn("<p>Texto com &lt;script&gt;alert(1)&lt;/script&gt; e o cookie <code>orzy_sessao</code>, "
                      "que continua na linha de baixo.</p>", texto)
        self.assertNotIn("<script>alert", texto)
        self.assertIn('<h2 id="1-o-que-e-o-orzy"><span class="lg-num">1</span> O que é o Orzy</h2>', texto)
        self.assertIn('<h2 id="2-contato-2">', texto, "dois títulos iguais não ficam com o mesmo id")
        self.assertIn('<a href="#1-o-que-e-o-orzy" data-secao="1-o-que-e-o-orzy"><span class="lg-indice-num">1</span>'
                      '<span>O que é o Orzy</span></a>', texto)
        self.assertIn("<li>um item que segue na linha seguinte;</li>", texto)
        self.assertIn('<a href="/privacidade#8-os-seus-direitos">Política</a>', texto, "um texto aponta para o outro")
        self.assertIn('<td role="cell" data-label="Dado">Código de renovação</td>'
                      '<td role="cell" data-label="Prazo">Não é guardado</td>', texto)
        self.assertNotIn("javascript:", texto)
        self.assertIn('<a href="https://www.gov.br/anpd" target="_blank" rel="noopener noreferrer">ANPD</a>', texto)
        self.assertIn('<a href="mailto:orzy.suporte@gmail.com">o Orzy</a>', texto, "e-mail sem abrir aba vazia")
        self.assertIn('<mark class="lg-pendente lg-preencher"><b>Preencher</b> CNPJ</mark>', texto)

    def test_textos_de_verdade_tem_indice_e_rodape(self):
        with override_settings(ORZY_PASTA_LEGAL=Path(__file__).resolve().parent.parent.parent / "docs" / "legal"):
            for caminho, nome in (("/privacidade", "Política de Privacidade"), ("/termos", "Termos de Uso")):
                texto = self.texto(self.abrir(caminho))
                self.assertIn(f"<title>{nome} · Orzy</title>", texto)
                self.assertIn('<nav class="lg-indice" aria-label="Nesta página">', texto)
                rodape = texto[texto.index('<footer class="sc-rodape'):]
                for link in ('href="/privacidade"', 'href="/termos"'):
                    self.assertIn(link, rodape, caminho)
