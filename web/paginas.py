"""Páginas do site, em HTML. Todo texto que vem do Mercado Livre passa por escape antes de entrar na página."""

from datetime import datetime, timedelta, timezone
from html import escape

import analise

BRASILIA = timezone(timedelta(hours=-3))  # o Brasil não tem horário de verão desde 2019
# Resumo que o Google e o WhatsApp mostram junto do link.
DESCRICAO = ("Conecte sua conta do Mercado Livre e veja quais anúncios vendem, quais não vendem e o que mudar em "
             "cada um. Sem instalar nada.")
CONTATO = "orzy.suporte@gmail.com"  # o mesmo da Política de Privacidade e dos Termos de Uso
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
<meta name="description" content="{escape(DESCRICAO)}">
<link rel="stylesheet" href="/static/estilo.css">
{atualiza}
</head>
<body>
<header class="topo"><a class="marca" href="/">Orzy</a><nav>{menu}</nav></header>
<main>{corpo}</main>
<footer class="rodape">O Orzy só lê os seus anúncios: não altera nada na sua conta.
Não somos o Mercado Livre. <a href="/privacidade">Política de Privacidade</a> · <a href="/termos">Termos de Uso</a>
· Contato: <a href="mailto:{CONTATO}">{CONTATO}</a></footer>
{arquivo_js}
</body>
</html>
"""


def inicio(logado, aviso=""):
    """Página inicial: o que o Orzy faz, como funciona, as situações, o que ele confere, dados e perguntas.

    Os números das situações e das regras vêm do analise.py, então a página acompanha qualquer ajuste nele.
    """
    if logado:
        botao = '<a class="botao botao-grande" href="/relatorio">Ver meu relatório</a>'
        aceite = ""
    else:
        botao = '<a class="botao botao-grande" href="/entrar">Conectar com Mercado Livre</a>'
        # Pedido dos Termos de Uso: o aviso fica junto de todo botão Conectar.
        aceite = ('<p class="aceite">Ao conectar, você aceita os <a href="/termos">Termos de Uso</a> e confirma '
                  'que leu a <a href="/privacidade">Política de Privacidade</a>.</p>')
    poucas = analise.POUCAS_VISITAS
    a_cada = round(1 / analise.CONVERSAO_BAIXA)  # 0.01 vira "1 venda a cada 100 visitas"
    dica = {nome: escape(texto) for nome, texto in analise.SITUACOES.items()}
    ordem = {nome: i for i, nome in enumerate(analise.ORDEM, 1)}  # a ordem em que aparecem no relatório
    corpo = f"""
{_aviso(aviso)}
<div class="inicio">

<section class="abertura" aria-labelledby="inicio-titulo">
  <div class="abertura-texto">
    <p class="sobretitulo">Para quem vende no Mercado Livre</p>
    <h1 id="inicio-titulo">Veja quais anúncios vendem e o que mudar em cada um</h1>
    <p class="lide">Conecte sua conta do Mercado Livre. O Orzy lê os seus anúncios ativos, com as visitas,
    as vendas e a nota de qualidade de cada um, e mostra o que mudar primeiro: título, fotos, ficha técnica,
    frete ou tipo de anúncio.</p>
    <p class="acao">{botao}<a class="link-secundario" href="#como-funciona">Ver como funciona</a></p>
    {aceite}
    <ul class="garantias">
      <li>Funciona no navegador, sem instalar nada</li>
      <li>Não muda nada nos seus anúncios</li>
      <li>Grátis durante o teste</li>
    </ul>
  </div>

  <figure class="exemplo">
    <figcaption><span>Exemplo de relatório</span><span>últimos 30 dias</span></figcaption>
    <ol class="exemplo-lista">
      <li>
        <p class="exemplo-titulo">Fone de Ouvido Bluetooth Sem Fio TWS com Microfone e Case</p>
        <p class="exemplo-dados"><span class="selo sit-vsv">Visita sem venda</span>
          <span>412 visitas</span><span>0 vendas</span></p>
        <ul>
          <li>Coloque pelo menos {analise.MIN_FOTOS} fotos, mostrando o produto de ângulos diferentes (tem 2).</li>
          <li>Ofereça frete grátis, se a margem permitir: o anúncio fica mais competitivo, mas o envio passa a ser
          pago por você.</li>
        </ul>
        <p class="exemplo-nota">Nota do Mercado Livre: Satisfatória (64/100)</p>
      </li>
      <li>
        <p class="exemplo-titulo">Suporte Celular Carro</p>
        <p class="exemplo-dados"><span class="selo sit-pv">Pouca visita</span>
          <span>9 visitas</span><span>0 vendas</span></p>
        <ul>
          <li>Mude o anúncio de Grátis para Clássico: o Grátis aparece pouco nas buscas. O Clássico cobra uma
          tarifa por venda.</li>
          <li>Título curto (21 de 60 caracteres): use o espaço com produto, marca, modelo e características
          principais, que são as palavras que as pessoas buscam.</li>
        </ul>
        <p class="exemplo-nota">Nota do Mercado Livre: Satisfatória (55/100)</p>
      </li>
      <li>
        <p class="exemplo-titulo">Garrafa Térmica Inox 1 Litro Para Café e Chá Quente e Fria</p>
        <p class="exemplo-dados"><span class="selo sit-vb">Vendendo bem</span>
          <span>380 visitas</span><span>19 vendas</span></p>
        <ul>
          <li>Está funcionando: use como modelo para os outros anúncios.</li>
        </ul>
        <p class="exemplo-nota">Nota do Mercado Livre: Profissional (91/100)</p>
      </li>
    </ol>
    <p class="exemplo-rodape">Anúncios fictícios, só para mostrar como o relatório aparece.</p>
  </figure>
</section>

<section class="secao" id="como-funciona" aria-labelledby="como-funciona-titulo">
  <h2 id="como-funciona-titulo">Como funciona</h2>
  <ol class="passos">
    <li>
      <h3>Conecte sua conta</h3>
      <p>Clique em Conectar com Mercado Livre e entre com a sua conta no próprio site do Mercado Livre.
      O Orzy não vê a sua senha.</p>
    </li>
    <li>
      <h3>Gere o relatório</h3>
      <p>Escolha o período, de 30 a 150 dias. O Orzy lê os anúncios ativos, as visitas, os pedidos pagos e a
      nota de qualidade de cada anúncio.</p>
    </li>
    <li>
      <h3>Mude o que importa</h3>
      <p>Comece pelos anúncios que mais precisam de mudança e faça os ajustes no Mercado Livre. Depois, gere
      outro relatório e compare no histórico.</p>
    </li>
  </ol>
</section>

<section class="secao" id="situacoes" aria-labelledby="situacoes-titulo">
  <h2 id="situacoes-titulo">Cada anúncio cai numa de cinco situações</h2>
  <p class="secao-lide">O Orzy compara as visitas e as vendas de cada anúncio no período. No relatório, as
  situações que mais valem a pena mexer aparecem primeiro.</p>
  <div class="matriz">
    <span class="eixo eixo-canto" aria-hidden="true"></span>
    <p class="eixo eixo-sem-venda" aria-hidden="true">Nenhuma venda</p>
    <p class="eixo eixo-com-venda" aria-hidden="true">Com vendas</p>
    <p class="eixo eixo-poucas" aria-hidden="true">Menos de {poucas} visitas</p>
    <p class="eixo eixo-muitas" aria-hidden="true">{poucas} visitas ou mais</p>
    <div class="situacao sit-vsv">
      <div class="situacao-topo">
        <h3 class="selo">Visita sem venda</h3>
        <span class="ordem">{ordem["VISITA SEM VENDA"]}º no relatório</span>
      </div>
      <p class="regra">{poucas} visitas ou mais e nenhuma venda</p>
      <p>{dica["VISITA SEM VENDA"]}</p>
    </div>
    <div class="situacao sit-cp">
      <div class="situacao-topo">
        <h3 class="selo">Converte pouco</h3>
        <span class="ordem">{ordem["CONVERTE POUCO"]}º no relatório</span>
      </div>
      <p class="regra">{poucas} visitas ou mais e menos de 1 venda a cada {a_cada} visitas</p>
      <p>{dica["CONVERTE POUCO"]}</p>
    </div>
    <div class="situacao sit-pv">
      <div class="situacao-topo">
        <h3 class="selo">Pouca visita</h3>
        <span class="ordem">{ordem["POUCA VISITA"]}º no relatório</span>
      </div>
      <p class="regra">Menos de {poucas} visitas e nenhuma venda</p>
      <p>{dica["POUCA VISITA"]}</p>
    </div>
    <div class="situacao sit-vpv">
      <div class="situacao-topo">
        <h3 class="selo">Vende, mas pouco visto</h3>
        <span class="ordem">{ordem["VENDE, MAS POUCO VISTO"]}º no relatório</span>
      </div>
      <p class="regra">Menos de {poucas} visitas e pelo menos 1 venda</p>
      <p>{dica["VENDE, MAS POUCO VISTO"]}</p>
    </div>
    <div class="situacao sit-vb">
      <div class="situacao-topo">
        <h3 class="selo">Vendendo bem</h3>
        <span class="ordem">{ordem["VENDENDO BEM"]}º no relatório</span>
      </div>
      <p class="regra">{poucas} visitas ou mais e pelo menos 1 venda a cada {a_cada} visitas</p>
      <p>{dica["VENDENDO BEM"]}</p>
    </div>
  </div>
</section>

<section class="secao" id="o-que-confere" aria-labelledby="o-que-confere-titulo">
  <h2 id="o-que-confere-titulo">O que o Orzy confere em cada anúncio</h2>
  <p class="secao-lide">As regras seguem o que o próprio Mercado Livre recomenda. Cada sugestão tem um peso
  e, dentro de cada situação, os anúncios com mais para mudar aparecem primeiro.</p>
  <dl class="conferidos">
    <div>
      <dt>Título <small>em geral, até {analise.TITULO_MAX_PADRAO} caracteres</small></dt>
      <dd>Se o título aproveita o limite da categoria com as palavras que as pessoas buscam, e se tem o que o
      Mercado Livre pede para não usar: frete, parcelamento, desconto, estado do produto, estoque (“pronta
      entrega”) ou símbolos.</dd>
    </div>
    <div>
      <dt>Fotos <small>pelo menos {analise.MIN_FOTOS}, com mais de {analise.LARGURA_ZOOM} px</small></dt>
      <dd>Se o anúncio tem fotos suficientes, de ângulos diferentes, e se elas são grandes o bastante para o
      zoom funcionar.</dd>
    </div>
    <div>
      <dt>Ficha técnica <small>obrigatórios primeiro</small></dt>
      <dd>Quais campos da categoria faltam preencher. Com a ficha completa, o anúncio aparece nos filtros
      da busca.</dd>
    </div>
    <div>
      <dt>Frete e tipo de anúncio <small>só quando há problema</small></dt>
      <dd>Frete grátis, trocar o Grátis pelo Clássico ou testar o Premium. Como custam dinheiro, só aparecem
      para anúncios com pouca visita ou pouca venda.</dd>
    </div>
    <div>
      <dt>Nota do Mercado Livre <small>de 0 a 100</small></dt>
      <dd>A nota de qualidade que o próprio Mercado Livre dá a cada anúncio (Básica, Satisfatória ou
      Profissional) e o que ele pede para melhorar.</dd>
    </div>
  </dl>
</section>

<section class="secao" id="seus-dados" aria-labelledby="seus-dados-titulo">
  <h2 id="seus-dados-titulo">Seus dados</h2>
  <div class="cartoes">
    <div class="cartao">
      <h3>Só leitura</h3>
      <p>O Orzy lê anúncios, visitas e vendas. Não altera título, preço, estoque nem nada da sua conta.</p>
    </div>
    <div class="cartao">
      <h3>Login pelo Mercado Livre</h3>
      <p>Você entra no site do próprio Mercado Livre e o Orzy não vê a sua senha. O acesso fica só na memória
      do servidor, enquanto a sessão dura.</p>
    </div>
    <div class="cartao">
      <h3>Você apaga quando quiser</h3>
      <p>O histórico guarda títulos e números dos anúncios, nunca dados de compradores. Você apaga tudo com
      um clique.</p>
    </div>
  </div>
  <p class="secao-pe">Leia a <a href="/privacidade">Política de Privacidade</a> e os
  <a href="/termos">Termos de Uso</a>.</p>
</section>

<section class="secao" id="perguntas" aria-labelledby="perguntas-titulo">
  <h2 id="perguntas-titulo">Perguntas frequentes</h2>
  <div class="perguntas">
    <details>
      <summary>Preciso instalar alguma coisa?</summary>
      <p>Não. O Orzy funciona no navegador, no computador ou no celular.</p>
    </details>
    <details>
      <summary>Preciso criar um app no Mercado Livre?</summary>
      <p>Não. Basta clicar em Conectar com Mercado Livre e autorizar o Orzy na tela do Mercado Livre.</p>
    </details>
    <details>
      <summary>O Orzy muda meus anúncios?</summary>
      <p>Não. Ele só lê os dados. As mudanças você faz no Mercado Livre, quando quiser.</p>
    </details>
    <details>
      <summary>De onde vêm as visitas e as vendas?</summary>
      <p>Do próprio Mercado Livre. As vendas são os pedidos pagos no período: cancelados e não pagos não
      contam. As visitas podem levar até 48 horas para aparecer.</p>
    </details>
    <details>
      <summary>Quanto tempo leva o relatório?</summary>
      <p>Depende de quantos anúncios você tem, porque o Orzy consulta as visitas de cada um. Pode fechar a
      página: o relatório continua sendo gerado.</p>
    </details>
    <details>
      <summary>Por que às vezes preciso conectar de novo?</summary>
      <p>Por segurança, o Orzy não guarda o seu acesso: ele fica só na memória do servidor enquanto a sessão
      dura. Depois, é só clicar em Conectar com Mercado Livre de novo.</p>
    </details>
    <details>
      <summary>Quanto custa?</summary>
      <p>Nada, enquanto o Orzy está em teste.</p>
    </details>
    <details>
      <summary>Funciona com a Shopee?</summary>
      <p>Ainda não. Por enquanto, só com o Mercado Livre.</p>
    </details>
    <details>
      <summary>O Orzy é do Mercado Livre?</summary>
      <p>Não. O Orzy é um serviço independente, que usa a API oficial do Mercado Livre com a sua autorização.</p>
    </details>
  </div>
</section>

<section class="chamada" aria-labelledby="chamada-titulo">
  <div>
    <h2 id="chamada-titulo">Descubra o que mudar primeiro</h2>
    <p>Conecte sua conta e gere o primeiro relatório. Você pode fechar a página enquanto ele é gerado.</p>
  </div>
  <div class="chamada-acao">
    <p class="acao">{botao}</p>
    {aceite}
  </div>
</section>

</div>"""
    return _pagina("O que mudar nos seus anúncios do Mercado Livre", corpo, logado=logado)


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
    # Os termos do Mercado Livre (5.3) pedem que o aplicativo diga quando os dados foram atualizados.
    gerado = ""
    if relatorio.gerado_em is not None:
        quando = relatorio.gerado_em.astimezone(BRASILIA).strftime("%d/%m/%Y às %H:%M")
        gerado = f'<p class="ajuda">Dados buscados no Mercado Livre em {quando} (horário de Brasília).</p>'
    corpo = f"""
<h1>Relatório dos últimos {relatorio.dias} dias</h1>
{gerado}
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
<p class="ajuda">Últimos {dados['dias']} dias · {dados['total']} anúncios.
Mostra como os anúncios estavam nesse dia: não é atualizado depois.</p>
<ul class="resumo">{_resumo_html(dados['resumo'])}</ul>
<div class="tabela"><table><thead><tr><th>Anúncio</th><th>Situação</th><th class=n>Visitas</th>
<th class=n>Vendas</th><th class=n>Sugestões</th></tr></thead><tbody>{linhas}</tbody></table></div>
<p><a href="/historico">Voltar ao histórico</a></p>"""
    return _pagina("Histórico", corpo, logado=True)


def texto_legal(titulo, html_do_texto):
    """Política de Privacidade ou Termos de Uso, já convertidos de docs/legal/ (ver legal.py)."""
    return _pagina(titulo, f'<article class="legal">{html_do_texto}</article>')


def texto_legal_ausente(nome):
    corpo = (f"<h1>{escape(nome)}</h1>"
             '<p class="aviso">Este texto ainda está sendo preparado.</p>')
    return _pagina(nome, corpo)


def erro(mensagem):
    corpo = (f'<h1>Algo não deu certo</h1><p class="aviso">{escape(mensagem)}</p>'
             '<p><a class="botao" href="/">Voltar ao início</a></p>')
    return _pagina("Erro", corpo)
