# 06 · Status

**Atualizado em:** 15/10/2026
**Fase atual:** 2, sugestões para cada anúncio: rodou no anúncio real em 15/10/2026. Falta conferir a ficha técnica
e as sugestões com o anúncio aberto no site ([02-roadmap.md](02-roadmap.md)).

## Onde parou

A fase 2 está pronta no programa do PC. O `meus_anuncios.py` agora lê de cada anúncio o título, as fotos, a ficha
técnica, o frete grátis e o tipo (Grátis, Clássico ou Premium), lê a nota de qualidade que o Mercado Livre dá ao anúncio
e diz o que mudar em cada um. As regras ficam no `painel-ml/analise.py`, separadas da coleta, para o site da fase 3
usar as mesmas.

Em 15/10/2026 o Nicolas rodou no microfone de lapela: a nota de qualidade veio (Profissional, 88/100), com o pedido
do Mercado Livre em português. A sugestão de fotos saiu duas vezes, a do Orzy e a do Mercado Livre, porque no Brasil
a regra das fotos não tem o nome da documentação. Isso foi corrigido, e a tela agora mostra também quantas fotos
e quantos campos da ficha técnica o anúncio tem. Falta rodar de novo para ver a contagem da ficha técnica e conferir
as sugestões com o anúncio aberto no site.

## Decisões de 14/10/2026

- O Orzy é para outros vendedores analisarem os próprios anúncios.
- O Nicolas comprou o domínio **orzy.com.br**.
- O Orzy vira site na **fase 3** (escolha do Nicolas). Até lá, o teste e a fase 2 seguem no programa do PC.
  Motivo: cada vendedor criar o próprio app é difícil demais, e o Client Secret não pode ir dentro de um programa distribuído.
- O app do Mercado Livre se chama "OrzyApp" e fica na conta do Nicolas. Ele serve para o teste e é editado na fase 3
  (Redirect URI do site), sem criar outro.
- O Claude faz o merge dos próprios PRs quando os testes do GitHub passam e avisa o que entrou.

## Feito

- Código do painel em `painel-ml/` (veio de uma conversa anterior com o Claude, que não está acessível aqui).
- Mercado Livre simulado em `testes/ml_simulado.py` e testes automáticos em `testes/test_painel.py`.
- Correções depois dos testes:
  - conexão que cai no meio da resposta fechava o programa com erro técnico em inglês: agora tenta de novo e, se não der, explica;
  - rede com bloqueio (escola, trabalho) que devolve uma página no lugar dos dados também fechava o programa: agora explica;
  - quando as visitas não podiam ser lidas (por exemplo, app sem permissão de métricas), o relatório saía todo "SEM DADOS" sem dizer por quê: agora mostra o motivo.
- LEIA-ME com como baixar do GitHub, permissões por área no app e os erros novos.
- LEIA-ME com o formulário novo do app (informações básicas e a tela "Configuração e scopes") e como autorizar
  com outra conta numa janela anônima. As mensagens do programa falam em "Refresh Token", o nome novo de "Acesso offline".
- Testes rodando sozinhos no GitHub a cada PR, no Windows (Python mais recente e 3.10) e no Linux: todos passam.
- Primeiro teste real (14/10/2026): app criado, login e relatório funcionando. Correções que saíram dele:
  - o `conectar.py` não mostra mais o Client Secret depois de colado (a chave apareceu num print do cmd);
  - se o que foi colado não tem o código, o `conectar.py` pede de novo em vez de fechar (o endereço acabou colado
    no cmd depois que o programa fechou);
  - o LEIA-ME explica melhor a barra de endereço do Explorador e onde achar a Chave secreta;
  - "1 anúncios encontrados" virou "1 anúncio encontrado".
- Fase 2 (15/10/2026):
  - `painel-ml/analise.py` com as situações e as regras de sugestão: título (curto para o limite da categoria,
    palavras que o Mercado Livre pede para não usar, estoque no título, símbolos), fotos (menos de 3, sem zoom),
    ficha técnica (campos que faltam, obrigatórios primeiro), frete grátis e tipo de anúncio (só para anúncio
    com problema, porque custam dinheiro) e o que o próprio Mercado Livre pede na nota de qualidade;
  - o relatório busca os campos novos de cada anúncio, a ficha técnica de cada categoria (uma vez por categoria)
    e a nota de qualidade (`/item/{id}/performance`, que substitui o `/health` antigo);
  - CSV com as colunas `o_que_mudar` e `qualidade_ml`, e os anúncios que mais precisam de mudança primeiro
    dentro de cada situação;
  - na tela, "Comece por estes" mostra até 10 anúncios com até 3 sugestões cada e a nota do Mercado Livre.
- Ajustes depois do teste real (15/10/2026):
  - o pedido de fotos do Mercado Livre, que no Brasil vem com outro nome de regra, não repete mais a sugestão do Orzy;
  - a tela e o CSV mostram quantas fotos e quantos campos da ficha técnica (preenchidos de total) cada anúncio tem;
  - se a ficha técnica do anúncio não vier na resposta do Mercado Livre, aparece "?" em vez de acusar campos faltando.

## O que foi testado (com dados simulados)

- Login com e sem PKCE, colando o endereço inteiro, só o código, ou o endereço sem `https://` e com aspas.
- Colar o exemplo `code=TG-...` e depois o endereço certo, no mesmo login.
- Endereço de outra tentativa de login, código usado duas vezes, Secret errado, recusa no navegador.
- Client Secret escondido ao colar num Prompt de Comando de verdade.
- Renovação do login: token vencido, token recusado antes da hora, refresh token de uso único salvo na hora.
- Erro 429, conexão caindo, sem internet, rede com bloqueio, sem permissão.
- Relatório: as 5 situações, período de 30, 60 e acima de 150 dias, pedidos pagos x cancelados x não pagos,
  mais de 50 pedidos, até 1000 e mais de 1000 anúncios (modo scan), multiget de no máximo 20,
  CSV aberto no Excel, conta sem anúncios, login vencido no meio do relatório.
- Fase 2:
  - cada regra de título, fotos, ficha técnica, frete e tipo, inclusive títulos que não podem dar falso alarme
    (100% algodão, -50°C, USB-C, "Descontinuado");
  - nota do Mercado Livre com regras pendentes e cumpridas, aviso (WARNING), nota ainda não calculada (404);
  - pedido do Mercado Livre igual a uma regra do Orzy: fica só o texto dele, com o peso maior;
  - ordem dos anúncios: dentro da mesma situação, quem tem mais para mudar vem antes;
  - limite do título vindo da categoria e ficha técnica lida uma vez por categoria;
  - sem permissão para a nota (para no primeiro anúncio e o relatório sai sem ela), 401 na nota (o login é
    renovado e salvo, e o relatório sai), nota que falha nos 3 primeiros anúncios (para de perguntar),
    erro ao ler a ficha técnica (o relatório sai sem as sugestões de ficha);
  - pedido de fotos do Mercado Livre com outro nome de regra, como veio no teste real: não repete a sugestão.
- Os dois programas rodando de verdade, como no Prompt de Comando, numa cópia da pasta.
- Testes rodados no Python 3.10, 3.11 e 3.13.

## Validado com dados reais (14 e 15/10/2026)

- [x] Criar o app no Mercado Livre (formulário novo: propósito, quantos usuários, logotipo, Fluxos OAuth, permissões por área).
- [x] `python conectar.py`: o Google mantém o código no endereço e o login dá certo, com PKCE e Refresh Token.
- [x] `python meus_anuncios.py`: roda sem erro, lê anúncios, visitas e vendas e salva o CSV.
- [x] Rodar no Windows de casa.
- [x] Trocar a chave secreta e entrar de novo com `python conectar.py --refazer`.
- [x] Abrir o CSV no Excel: colunas certas, preço com vírgula, link do anúncio.
- [ ] Conferir visitas e vendas com o painel do Mercado Livre numa conta com movimento.
- [ ] Rodar numa conta com mais anúncios e vendas (um vendedor que autorize o app).
- [x] Fase 2: rodar no microfone de lapela (15/10/2026). A nota de qualidade veio (Profissional, 88/100), o pedido
  do Mercado Livre veio em português e as fotos foram lidas (1 foto).
- [ ] Fase 2: ver a contagem da ficha técnica na tela (linha "Ficha técnica: X de Y campos").
- [ ] Fase 2: conferir as sugestões com o anúncio aberto no site do Mercado Livre.

## Próximo passo

1. Nicolas: baixar o ZIP de novo do GitHub. Para não fazer login de novo, copiar o `config.json` e o `tokens.json`
   da pasta `painel-ml` usada por último para a nova.
2. Nicolas: rodar `python meus_anuncios.py`, mandar o texto do que apareceu no cmd e conferir, no anúncio aberto
   no site, o número de fotos e se a ficha técnica está completa.
3. Claude: ajustar o que precisar e marcar a fase 2 como concluída.
4. Quando der, rodar numa conta com mais anúncios e vendas, de um vendedor que autorize o app.

Na conversa, mandar só o texto do que apareceu no cmd, sem print. **Nunca** mandar o Client Secret,
o `config.json` nem o `tokens.json`.

## Em aberto

- Qual vendedor com mais anúncios vai testar.
- O que "propósito" e "quantos usuários" do formulário do app mudam: a documentação do Mercado Livre não fala.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
