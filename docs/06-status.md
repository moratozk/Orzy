# 06 · Status

**Atualizado em:** 15/10/2026
**Fase atual:** 3, construindo o site (código em rascunho no PR #5, sem merge). A fase 2 está concluída.
Plano e custos em [07-fase-3-plano.md](07-fase-3-plano.md). Nada vai ao ar antes de o site estar quase pronto.

## Quem faz o quê (15/10/2026)

- **Site: código e login**: `web/`, `testes/test_site.py`, `docs/07-fase-3-plano.md`, este arquivo e o PR #5 (rascunho).
- **Página inicial do site**: entregou a página, que já está no PR #5. Thread encerrada.
- **Privacidade e termos**: `docs/legal/` (PR #6, mesclado em 15/10/2026). O site mostra esses textos em `/privacidade`
  e `/termos`.
- **Hospedagem e domínio**: hospedagem, deploy, DNS, Redirect URI e Client Secret do OrzyApp. A recomendação está em
  `/mnt/project-files/orzy/hospedagem-recomendacao.md`; o resto espera o lançamento e o ok do Nicolas.
- Pesquisa anterior de hospedagem e LGPD: `/mnt/project-files/orzy/hospedagem-e-lgpd.md`.
- Domínio: orzy.com.br responde com uma página temporária que o Nicolas colocou no Firebase (DNS no Registro.br).

## Onde parou

A fase 2 está concluída. Em 15/10/2026 o Nicolas rodou no microfone de lapela: a nota de qualidade veio
(Profissional, 88/100), com o pedido do Mercado Livre em português. A sugestão de fotos saiu duas vezes; isso foi
corrigido no PR #4, que foi mesclado. O anúncio aberto no site confere com as sugestões: 1 foto, título curto
e frete grátis, que é o correto para ele.

Falta uma coisa pequena, que não segura a fase: ver na próxima rodada a contagem da ficha técnica na tela
("Ficha técnica: X de Y campos").

A fase 3 começou só como planejamento e rascunho, porque o Nicolas pediu para avançar enquanto estava fora.
Nada foi publicado, contratado nem mudado no app do Mercado Livre. Ele decide hospedagem, app, LGPD e limites.

Em 15/10/2026 o Nicolas aprovou a página inicial como primeiro protótipo (logo e cores vêm depois) e decidiu que o
site só vai ao ar quando estiver quase pronto ("95% concluído"), sem endereço temporário. O foco agora é construir
o site e o servidor.

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
  - `docs/07-fase-3-plano.md`: plano em 5 passos, custos em reais, LGPD e decisões que faltam;
  - página inicial (aprovada como primeiro protótipo em 15/10/2026), com o aviso de aceite dos Termos junto de cada
    botão Conectar;
  - `/privacidade` e `/termos` mostram os textos de `docs/legal/`, com links no rodapé de todas as páginas;
  - o resultado mostra a data e a hora em que os dados foram buscados (termos do Mercado Livre, item 5.3);
  - o histórico com mais de 365 dias é apagado todo dia, e não só quando o servidor liga;
  - recomendação de hospedagem com custos em reais (thread "Hospedagem e domínio").

## O que foi testado (com dados simulados)

- Programa do PC: login com e sem PKCE, Client Secret escondido ao colar, renovação do login, erros 429, sem internet,
  rede com bloqueio, sem permissão, relatórios de 30 a 150 dias, até 1000 e mais de 1000 anúncios (modo scan),
  CSV aberto no Excel, conta sem anúncios, nota de qualidade com regras pendentes, aviso e ainda não calculada,
  pedido de fotos com outro nome de regra, ordem dos anúncios e limites de chamadas.
- Site (fase 3): login inteiro (estado do OAuth, PKCE, retorno), token que não é gravado em disco, relatório
  com título que tem HTML (sai escapado), CSV com BOM, isolamento entre contas, token vencido sem renovação
  escondida, pedido de outro site recusado, um relatório por conta, histórico com confirmação para apagar,
  cabeçalhos de segurança, uma ida e volta por HTTP real, página inicial com e sem login, textos legais lidos de
  `docs/legal/` (com escape), rodapé com os dois textos, data do relatório em horário de Brasília e limpeza diária
  do histórico, que continua depois de um erro.
- Testes rodados no Python 3.10 e 3.13 (95: 64 do PC e 31 do site). Quebrar de propósito a checagem do estado do
  OAuth, o escape (de títulos e dos textos legais), o rodapé, a hora de Brasília ou a limpeza diária faz os testes
  falharem.

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

1. Nicolas: nada urgente. As decisões de [07-fase-3-plano.md](07-fase-3-plano.md) (hospedagem, app, limites,
   contato, revisão de advogado, beta ou público) ficam para quando o site estiver quase pronto.
2. Nicolas: quando puder, baixar o ZIP de novo do GitHub. Para não fazer login de novo, copiar o `config.json` e o
   `tokens.json` da pasta `painel-ml` usada por último para a nova. Rodar `python meus_anuncios.py` e mandar o
   texto do que apareceu no cmd (sem print). Ver a linha "Ficha técnica: X de Y campos".
3. Site: seguir construindo o que não depende de decisão. As mudanças da hospedagem entram quando ela for escolhida,
   e a identidade visual (logo e cores) quando o Nicolas trouxer.

Na conversa, mandar só o texto do que apareceu no cmd, sem print. **Nunca** mandar o Client Secret,
o `config.json`, o `tokens.json` nem o banco do site.

## Em aberto

- Qual vendedor com mais anúncios vai testar.
- O que "propósito" e "quantos usuários" do formulário do app mudam: a documentação do Mercado Livre não fala.
- Hospedagem: Google, com Cloud Run e Firestore em São Paulo (recomendado, R$ 0 no teste), ou Render (cerca de
  R$ 37/mês). No Google, falta escolher a porta de entrada; o Firebase Hosting do orzy.com.br fica fora das cláusulas
  da ANPD. Decide na hora de lançar.
- Termos do Mercado Livre para desenvolvedores (lidos em 15/10/2026): não fixam prazo para guardar dados. O histórico
  de 12 meses, privado e que o vendedor apaga, é compatível na leitura mais razoável; confirmar com advogado.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
