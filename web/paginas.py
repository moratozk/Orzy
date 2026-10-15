"""Páginas do site, em HTML. Todo texto que vem do Mercado Livre passa por escape antes de entrar na página."""

from datetime import datetime, timedelta, timezone
from html import escape

import analise

BRASILIA = timezone(timedelta(hours=-3))  # o Brasil não tem horário de verão desde 2019
MAX_PRIORIDADES = 10
SUGESTOES_POR_ANUNCIO = 3


def _t(valor):
    return "?" if valor is None else escape(str(valor))


def _data(iso):
    try:
        return datetime.fromisoformat(iso).astimezone(BRASILIA).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return "?"


def _aviso(texto):
    return f'<p class="aviso">{escape(texto)}</p>' if texto else ""


def _link(linha):
    titulo = escape(linha["titulo"] or "(sem título)")
    url = linha.get("link") or ""
    if url.startswith("https://"):
        return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{titulo}</a>'
    return titulo


def _resumo_html(contagem):
    return "".join(f"<li><span>{escape(s)}</span><strong>{n}</strong></li>" for s, n in contagem.items() if n)


def _pagina(titulo, corpo, logado=False, script=None, atualizar=None):
    if logado:
        menu = ('<a href="/relatorio">Relatório</a>'
                '<a href="/historico">Histórico</a>'
                '<form method="post" action="/sair"><button class="link" type="submit">Sair</button></form>')
    else:
        menu = '<a href="/privacidade">Privacidade</a>'
    atualiza = f'<meta http-equiv="refresh" content="{int(atualizar)}">' if atualizar else ""
    arquivo_js = f'<script src="/static/{script}" defer></script>' if script else ""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)} · Orzy</title>
<link rel="stylesheet" href="/static/estilo.css">
{atualiza}
</head>
<body>
<header class="topo"><a class="marca" href="/">Orzy</a><nav>{menu}</nav></header>
<main>{corpo}</main>
<footer class="rodape">O Orzy só lê os seus anúncios: não altera nada na sua conta.
Não somos o Mercado Livre. <a href="/privacidade">Privacidade e dados</a></footer>
{arquivo_js}
</body>
</html>
"""


def inicio(logado, aviso=""):
    botao = ('<a class="botao" href="/relatorio">Ver meu relatório</a>' if logado
             else '<a class="botao" href="/entrar">Conectar com Mercado Livre</a>')
    corpo = f"""
{_aviso(aviso)}
<section>
  <h1>Veja quais anúncios vendem e o que mudar em cada um</h1>
  <p>Entre com a sua conta do Mercado Livre. O Orzy mostra os seus anúncios ativos com visitas, vendas
  e a nota de qualidade que o próprio Mercado Livre dá a cada um, e diz o que mudar primeiro.</p>
  <p>{botao}</p>
</section>
<section class="cartoes">
  <div class="cartao"><h2>Só leitura</h2>
    <p>O Orzy lê anúncios, visitas e vendas. Não altera título, preço, estoque nem nada da sua conta.</p></div>
  <div class="cartao"><h2>Login só na sessão</h2>
    <p>O acesso fica na memória do servidor enquanto a sua sessão dura. Não é gravado em arquivo nem no seu navegador.</p></div>
  <div class="cartao"><h2>Você apaga quando quiser</h2>
    <p>Os relatórios guardados no histórico podem ser apagados com um clique.
    Veja a <a href="/privacidade">política de privacidade</a>.</p></div>
</section>"""
    return _pagina("Início", corpo, logado=logado)


def formulario(usuario, opcoes, aviso="", em_andamento=None):
    apelido = escape(usuario.get("apelido") or "sua conta")
    escolhas = "".join(f'<option value="{d}"{" selected" if d == opcoes[0] else ""}>últimos {d} dias</option>'
                       for d in opcoes)
    andamento_html = ""
    if em_andamento is not None:
        andamento_html = (f'<p class="aviso">Você tem um relatório sendo gerado. '
                          f'<a href="/relatorio/{escape(em_andamento.id)}">Ver andamento</a></p>')
    corpo = f"""
<h1>Relatório da conta {apelido}</h1>
{_aviso(aviso)}
{andamento_html}
<form class="cartao" method="post" action="/relatorio/gerar">
  <label for="dias">Período das visitas e vendas</label>
  <select id="dias" name="dias">{escolhas}</select>
  <p class="ajuda">O Orzy lê as visitas de cada anúncio, então um relatório com muitos anúncios leva alguns minutos.
  Se você sair da página, o relatório continua sendo gerado.</p>
  <p><button class="botao" type="submit">Gerar relatório</button></p>
</form>"""
    return _pagina("Relatório", corpo, logado=True)


def _contagem(relatorio):
    return f"{relatorio.feitos} de {relatorio.total}" if relatorio.total else ""


def andamento(relatorio):
    corpo = f"""
<h1>Gerando seu relatório</h1>
<p id="etapa">{escape(relatorio.etapa)}</p>
<progress id="barra" max="{max(relatorio.total, 1)}" value="{relatorio.feitos}"></progress>
<p id="contagem" class="ajuda">{_contagem(relatorio)}</p>
<p class="ajuda">Pode fechar esta página: o relatório continua sendo gerado.
Volte em <a href="/relatorio">Relatório</a> para vê-lo.</p>
<div id="dados" data-andamento="/relatorio/{escape(relatorio.id)}/andamento.json"
     data-destino="/relatorio/{escape(relatorio.id)}" hidden></div>"""
    return _pagina("Gerando relatório", corpo, logado=True, script="andamento.js", atualizar=10)


def _cartao_anuncio(linha):
    textos = [s["texto"] for s in linha["sugestoes"]] or [linha["o_que_olhar"]]
    itens = "".join(f"<li>{escape(t)}</li>" for t in textos[:SUGESTOES_POR_ANUNCIO])
    mais = len(textos) - SUGESTOES_POR_ANUNCIO
    rodape = f'<p class="ajuda">(mais {mais} no CSV)</p>' if mais > 0 else ""
    return f"""
<article class="anuncio">
  <h3>{_link(linha)}</h3>
  <p class="ajuda">{_t(linha['visitas'])} visitas · {_t(linha['vendas'])} vendas · {escape(linha['situacao'])}</p>
  <p class="ajuda">Nota do Mercado Livre: {escape(linha['qualidade'])} · Fotos: {_t(linha['fotos'])} ·
  Ficha técnica: {escape(linha['ficha'])}</p>
  <ul>{itens}</ul>
  {rodape}
</article>"""


def _linha_tabela(linha):
    mudancas = " · ".join(s["texto"] for s in linha["sugestoes"]) or "Nenhuma mudança sugerida"
    return (f"<tr><td>{_link(linha)}</td><td>{escape(linha['situacao'])}</td>"
            f"<td class=n>{_t(linha['visitas'])}</td><td class=n>{_t(linha['vendas'])}</td>"
            f"<td>{escape(linha['qualidade'])}</td><td class=n>{_t(linha['fotos'])}</td>"
            f"<td>{escape(linha['ficha'])}</td><td>{escape(mudancas)}</td></tr>")


def _tabela(linhas):
    cabecalho = ("<tr><th>Anúncio</th><th>Situação</th><th class=n>Visitas</th><th class=n>Vendas</th>"
                 "<th>Nota do ML</th><th class=n>Fotos</th><th>Ficha técnica</th><th>O que mudar</th></tr>")
    corpo = "".join(_linha_tabela(l) for l in linhas)
    return f'<div class="tabela"><table><thead>{cabecalho}</thead><tbody>{corpo}</tbody></table></div>'


def resultado(relatorio):
    linhas = relatorio.linhas
    contagem = {s: sum(1 for l in linhas if l["situacao"] == s) for s in analise.ORDEM}
    com_problema = analise.PROBLEMA_DE_VENDA | analise.PROBLEMA_DE_VISITA
    prioridade = [l for l in linhas if l["sugestoes"] or l["situacao"] in com_problema][:MAX_PRIORIDADES]
    cartoes = "".join(_cartao_anuncio(l) for l in prioridade) or \
        '<p class="ajuda">Nenhum anúncio com sugestão de mudança neste período.</p>'
    tabela = _tabela(linhas) if linhas else ""
    corpo = f"""
<h1>Relatório dos últimos {relatorio.dias} dias</h1>
{_aviso(relatorio.aviso)}
{_aviso(relatorio.mensagem)}
<ul class="resumo">{_resumo_html(contagem)}</ul>
<p><a class="botao" href="/relatorio/{escape(relatorio.id)}/csv">Baixar planilha (CSV)</a>
<a class="botao secundario" href="/relatorio">Gerar outro</a></p>
<h2>Comece por estes</h2>
{cartoes}
<h2>Todos os anúncios</h2>
{tabela}"""
    return _pagina("Relatório", corpo, logado=True)


def relatorio_com_erro(relatorio):
    corpo = f"""
<h1>Não deu para gerar o relatório</h1>
{_aviso(relatorio.mensagem)}
<p><a class="botao" href="/relatorio">Tentar de novo</a></p>"""
    return _pagina("Relatório", corpo, logado=True)


def historico(lista):
    if lista:
        linhas = "".join(
            f"<tr><td><a href='/historico/{r['id']}'>{_data(r['criado_em'])}</a></td>"
            f"<td class=n>{r['dias']} dias</td><td class=n>{r['total']}</td>"
            f"<td>{escape('; '.join(f'{s}: {n}' for s, n in r['resumo'].items() if n) or '-')}</td></tr>"
            for r in lista)
        tabela = ('<div class="tabela"><table><thead><tr><th>Data</th><th class=n>Período</th>'
                  '<th class=n>Anúncios</th><th>Situações</th></tr></thead>'
                  f'<tbody>{linhas}</tbody></table></div>')
    else:
        tabela = '<p class="ajuda">Você ainda não tem relatórios guardados.</p>'
    corpo = f"""
<h1>Histórico</h1>
<p class="ajuda">Relatórios guardados. Abra cada um para ver como os anúncios estavam naquele dia.</p>
{tabela}
<form class="cartao" method="post" action="/historico/apagar">
  <label><input type="checkbox" name="confirmo" value="on" required>
  Entendo que todo o histórico será apagado</label>
  <p><button class="botao secundario" type="submit">Apagar meu histórico</button></p>
</form>"""
    return _pagina("Histórico", corpo, logado=True)


def historico_relatorio(dados):
    linhas = "".join(
        f"<tr><td>{escape(a['titulo'] or '(sem título)')}</td><td>{escape(a['situacao'])}</td>"
        f"<td class=n>{_t(a['visitas'])}</td><td class=n>{_t(a['vendas'])}</td>"
        f"<td class=n>{a['pontos']}</td></tr>"
        for a in dados["anuncios"])
    corpo = f"""
<h1>Relatório de {_data(dados['criado_em'])}</h1>
<p class="ajuda">Últimos {dados['dias']} dias · {dados['total']} anúncios</p>
<ul class="resumo">{_resumo_html(dados['resumo'])}</ul>
<div class="tabela"><table><thead><tr><th>Anúncio</th><th>Situação</th><th class=n>Visitas</th>
<th class=n>Vendas</th><th class=n>Sugestões</th></tr></thead><tbody>{linhas}</tbody></table></div>
<p><a href="/historico">Voltar ao histórico</a></p>"""
    return _pagina("Histórico", corpo, logado=True)


def privacidade():
    corpo = """
<h1>Privacidade e dados</h1>
<p class="aviso">Rascunho: esta página ainda vai ser revisada antes do lançamento para o público.</p>

<h2>Quem é responsável</h2>
<p>[Nome completo e CPF ou CNPJ do responsável pelo Orzy, a preencher.]</p>

<h2>Quais dados usamos</h2>
<p>Ao conectar a sua conta, recebemos do Mercado Livre o número do seu usuário e o seu apelido.
Para gerar o relatório, lemos os seus anúncios ativos (título, preço, estoque, fotos, ficha técnica e tipo de anúncio),
as visitas de cada um no período escolhido, os pedidos pagos do período e a nota de qualidade de cada anúncio.</p>
<p>Dos pedidos usamos só a quantidade vendida de cada anúncio. Não guardamos dados pessoais de compradores.</p>

<h2>Para que usamos</h2>
<p>Só para gerar o relatório e as sugestões que você pediu e para mostrar o seu histórico.</p>

<h2>Login e sessão</h2>
<p>O token de acesso do Mercado Livre fica na memória do servidor, enquanto a sua sessão dura.
Não guardamos o token de atualização. Quando a sessão acaba ou o servidor reinicia, você conecta de novo.</p>

<h2>Histórico</h2>
<p>Guardamos, por relatório, a data, o período, a contagem de anúncios por situação e, para cada anúncio,
o número, o título, as visitas, as vendas, a situação e os pontos de sugestão.
Você apaga tudo na página Histórico. Relatórios com mais de 12 meses são apagados automaticamente.</p>

<h2>Com quem compartilhamos</h2>
<p>Não vendemos nem compartilhamos os seus dados. [A confirmar: fornecedor de hospedagem que guarda os dados em nosso nome.]</p>

<h2>Seus direitos</h2>
<p>Você pode pedir para ver, corrigir ou apagar os seus dados, e saber com quem eles foram compartilhados.
Para apagar o histórico, use a página Histórico. Para o restante, escreva para o contato abaixo.</p>

<h2>Contato</h2>
<p>[E-mail de contato, a definir.]</p>
"""
    return _pagina("Privacidade", corpo)


def erro(mensagem):
    corpo = (f'<h1>Algo não deu certo</h1><p class="aviso">{escape(mensagem)}</p>'
             '<p><a class="botao" href="/">Voltar ao início</a></p>')
    return _pagina("Erro", corpo)
