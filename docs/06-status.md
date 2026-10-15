# 06 · Status

**Atualizado em:** 15/10/2026
**Fase atual:** 3, planejamento e código em rascunho do site (PR, sem merge). A fase 2 está concluída.
Plano e custos em [07-fase-3-plano.md](07-fase-3-plano.md).

## Onde parou

A fase 2 está concluída. Em 15/10/2026 o Nicolas rodou no microfone de lapela: a nota de qualidade veio
(Profissional, 88/100), com o pedido do Mercado Livre em português. A sugestão de fotos saiu duas vezes; isso foi
corrigido no PR #4, que foi mesclado. O anúncio aberto no site confere com as sugestões: 1 foto, título curto
e frete grátis, que é o correto para ele.

Falta uma coisa pequena, que não segura a fase: ver na próxima rodada a contagem da ficha técnica na tela
("Ficha técnica: X de Y campos").

A fase 3 começou só como planejamento e rascunho, porque o Nicolas pediu para avançar enquanto estava fora.
Nada foi publicado, contratado nem mudado no app do Mercado Livre. Ele decide hospedagem, app, LGPD e limites.

## Decisões de 14/10/2026

- O Orzy é para outros vendedores analisarem os próprios anúncios.
- O Nicolas comprou o domínio **orzy.com.br**.
- O Orzy vira site na **fase 3** (escolha do Nicolas). Até lá, o teste e a fase 2 seguem no programa do PC.
  Motivo: cada vendedor criar o próprio app é difícil demais, e o Client Secret não pode ir dentro de um programa distribuído.
- O app do Mercado Livre se chama "OrzyApp" e fica na conta do Nicolas. Ele serve para o teste e é editado na fase 3
  (Redirect URI do site), sem criar outro.
- O Claude faz o merge dos próprios PRs quando os testes do GitHub passam e avisa o que entrou.
  Exceção: o PR do site fica em rascunho até o Nicolas aprovar o plano da fase 3.

## Feito

- Código do painel em `painel-ml/` (veio de uma conversa anterior com o Claude, que não está acessível aqui).
- Mercado Livre simulado em `testes/ml_simulado.py` e testes automáticos em `testes/test_painel.py`.
- Correções depois dos testes: conexão que cai no meio, rede com bloqueio, relatório "SEM DADOS" sem motivo, e outras
  (ver o histórico do git).
- LEIA-ME com como baixar do GitHub, permissões por área no app, o formulário novo do app e os erros novos.
- Testes rodando sozinhos no GitHub a cada PR, no Windows (Python mais recente e 3.10) e no Linux.
- Primeiro teste real (14/10/2026): app criado, login e relatório funcionando. Correções que saíram dele:
  - o `conectar.py` não mostra mais o Client Secret depois de colado (a chave apareceu num print do cmd);
  - se o que foi colado não tem o código, o `conectar.py` pede de novo em vez de fechar;
  - o LEIA-ME explica melhor a barra de endereço do Explorador e onde achar a Chave secreta;
  - "1 anúncios encontrados" virou "1 anúncio encontrado".
- Fase 2 (PR #3 e #4, mesclados em 15/10/2026):
  - `painel-ml/analise.py` com as situações e as regras de sugestão (título, fotos, ficha técnica, frete, tipo de
    anúncio e a nota de qualidade do próprio Mercado Livre);
  - o relatório busca os campos novos de cada anúncio, a ficha técnica de cada categoria e a nota de qualidade
    (`/item/{id}/performance`, que substitui o `/health` antigo);
  - CSV com as colunas `o_que_mudar`, `qualidade_ml`, `fotos` e `ficha_tecnica`;
  - na tela, "Comece por estes" mostra até 10 anúncios com até 3 sugestões cada, a nota, as fotos e a ficha técnica;
  - o pedido de fotos do Mercado Livre, que no Brasil vem com outro nome de regra, não repete mais a sugestão do Orzy.
- Fase 3, em rascunho (PR, sem merge):
  - `web/`: o site (login com PKCE, relatório em segundo plano, histórico, páginas e servidor, só biblioteca padrão);
  - `painel-ml/`: o login e a coleta ganharam versões que o site usa sem gravar em arquivo; o PC continua igual;
  - `testes/test_site.py`: testes do site contra o Mercado Livre simulado;
  - `docs/07-fase-3-plano.md`: plano em 5 passos, custos em reais, LGPD e decisões que faltam.

## O que foi testado (com dados simulados)

- Programa do PC: login com e sem PKCE, Client Secret escondido ao colar, renovação do login, erros 429, sem internet,
  rede com bloqueio, sem permissão, relatórios de 30 a 150 dias, até 1000 e mais de 1000 anúncios (modo scan),
  CSV aberto no Excel, conta sem anúncios, nota de qualidade com regras pendentes, aviso e ainda não calculada,
  pedido de fotos com outro nome de regra, ordem dos anúncios e limites de chamadas.
- Site (fase 3): login inteiro (estado do OAuth, PKCE, retorno), token que não é gravado em disco, relatório
  com título que tem HTML (sai escapado), CSV com BOM, isolamento entre contas, token vencido sem renovação
  escondida, pedido de outro site recusado, um relatório por conta, histórico com confirmação para apagar,
  cabeçalhos de segurança e uma ida e volta por HTTP real.
- Testes rodados no Python 3.10 e 3.13. Quebrar de propósito a checagem do estado do OAuth e o escape de títulos
  faz os testes falharem.

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
- [x] Fase 2: conferir as sugestões com o anúncio aberto no site (15/10/2026: 1 foto, título curto e frete grátis batem).
- [ ] Fase 2: ver a contagem da ficha técnica na tela (linha "Ficha técnica: X de Y campos"). Não segura a fase.
- [ ] Fase 3: o login do site com o Mercado Livre de verdade (depende da Redirect URI do site no app).

## Próximo passo

1. Nicolas: responder as decisões de [07-fase-3-plano.md](07-fase-3-plano.md) (hospedagem, app, limites, contato,
   revisão de advogado, beta ou público). Uma palavra por item basta.
2. Nicolas: quando puder, baixar o ZIP de novo do GitHub. Para não fazer login de novo, copiar o `config.json` e o
   `tokens.json` da pasta `painel-ml` usada por último para a nova. Rodar `python meus_anuncios.py` e mandar o
   texto do que apareceu no cmd (sem print). Ver a linha "Ficha técnica: X de Y campos".
3. Claude: com o ok do passo 1 e 2 da fase 3, publicar num endereço de teste e testar com a conta do Nicolas.

Na conversa, mandar só o texto do que apareceu no cmd, sem print. **Nunca** mandar o Client Secret,
o `config.json`, o `tokens.json` nem o banco do site.

## Em aberto

- Qual vendedor com mais anúncios vai testar.
- O que "propósito" e "quantos usuários" do formulário do app mudam: a documentação do Mercado Livre não fala.
- Os termos do Mercado Livre sobre guardar dados de vendedores: a página não abriu no dia 15/10/2026.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
