# 06 · Status

**Atualizado em:** 14/10/2026
**Fase atual:** 1 concluída. Próxima: 2, sugestões para cada anúncio ([02-roadmap.md](02-roadmap.md))

## Onde parou

Primeiro teste com dados reais feito em 14/10/2026, no Windows de casa. O app "OrzyApp" foi criado,
o `conectar.py` fez o login (com PKCE e Refresh Token) e o `meus_anuncios.py` leu 1 anúncio ativo da conta
conectada, com visitas e vendas sem erro (resultado: POUCA VISITA).

A chave secreta, que apareceu em prints durante o teste, já foi trocada, e o login foi refeito com a chave nova.
O CSV saiu certo no Excel: o anúncio (um microfone de lapela, R$ 79,90, 10 em estoque) teve 0 visitas e 0 vendas
em 30 dias. Com números zerados, a conferência das visitas e vendas fica para uma conta com movimento.

## Decisões de 14/10/2026

- O Orzy é para outros vendedores analisarem os próprios anúncios.
- O Nicolas comprou o domínio **orzy.com.br**.
- O Orzy vira site na **fase 3** (escolha do Nicolas). Até lá, o teste e a fase 2 seguem no programa do PC.
  Motivo: cada vendedor criar o próprio app é difícil demais, e o Client Secret não pode ir dentro de um programa distribuído.
- O app do Mercado Livre se chama "OrzyApp" e fica na conta do Nicolas. Ele serve para o teste e é editado na fase 3
  (Redirect URI do site), sem criar outro.

## Feito

- Código do painel em `painel-ml/` (veio de uma conversa anterior com o Claude, que não está acessível aqui).
- Mercado Livre simulado em `testes/ml_simulado.py` e 36 testes em `testes/test_painel.py`.
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
- Os dois programas rodando de verdade, como no Prompt de Comando, numa cópia da pasta.

## Validado com dados reais (14/10/2026)

- [x] Criar o app no Mercado Livre (formulário novo: propósito, quantos usuários, logotipo, Fluxos OAuth, permissões por área).
- [x] `python conectar.py`: o Google mantém o código no endereço e o login dá certo, com PKCE e Refresh Token.
- [x] `python meus_anuncios.py`: roda sem erro, lê anúncios, visitas e vendas e salva o CSV.
- [x] Rodar no Windows de casa.
- [x] Trocar a chave secreta e entrar de novo com `python conectar.py --refazer`.
- [x] Abrir o CSV no Excel: colunas certas, preço com vírgula, link do anúncio.
- [ ] Conferir visitas e vendas com o painel do Mercado Livre numa conta com movimento.
- [ ] Rodar numa conta com mais anúncios e vendas (um vendedor que autorize o app).

## Próximo passo

1. Nicolas: fazer o merge do PR #2 (correções do primeiro teste e plano novo).
2. Claude: mostrar o plano da fase 2 e esperar o ok antes de escrever o código.
3. Quando der, rodar numa conta com mais anúncios e vendas, de um vendedor que autorize o app.

Na conversa, mandar só o texto do que apareceu no cmd, sem print. **Nunca** mandar o Client Secret,
o `config.json` nem o `tokens.json`.

## Em aberto

- Qual vendedor com mais anúncios vai testar.
- O que "propósito" e "quantos usuários" do formulário do app mudam: a documentação do Mercado Livre não fala.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
