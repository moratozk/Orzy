# 06 · Status

**Atualizado em:** 15/10/2026
**Fase atual:** 3, construindo o site (código em rascunho no PR #5, sem merge). A fase 2 está concluída.
Plano e custos em [07-fase-3-plano.md](07-fase-3-plano.md). Nada vai ao ar antes de o site estar quase pronto.

## Quem faz o quê (15/10/2026, nova divisão)

Dividido de novo a pedido do Nicolas em 15/10/2026 (texto completo em
`/mnt/project-files/orzy/plano/divisao-das-tarefas.md`). Duas frentes não mexem nos mesmos arquivos ao mesmo
tempo, e poucas ficam ativas de cada vez, porque cada thread ativa gasta o limite de uso do plano do Nicolas.

Agora:

- **Site: código e login**: nesta ordem, a busca e o filtro em "Todos os anúncios"; a logo e as cores da Anel no
  site base quando a thread da marca avisar (favicon, ícones, imagem de compartilhamento e a fonte Geist servida
  pelo próprio site); as contagens do beta (contas conectadas, relatórios sem erro e anúncios por conta, só
  contagens); depois, o visual final que a marca entregar e o Nicolas aprovar. Arquivos: `web/`, `testes/`,
  `painel-ml/`, `docs/01` a `docs/07` (menos `docs/legal/`), o README e o PR #5 (rascunho).
- **Identidade visual e logo**: fecha os arquivos da Anel (favicon, ícones, imagens, cores claro e escuro, guia) e
  avisa a thread do código; depois desenha o visual final das páginas como prévia e CSS prontos, sem estilo ou
  script dentro do HTML e sem nada de fora (tudo sai de `/static`). Arquivos em `/mnt/project-files/orzy/marca/`;
  não mexe em `web/`. A troca no site espera o ok do Nicolas na prévia.

Esperando:

- **Privacidade e termos**: `docs/legal/` (PR #6, #7, #8 e #9, mesclados em 15/10/2026); o site mostra esses
  textos em `/privacidade` e `/termos`. Quando o site base fechar, reconfere a Política e os Termos contra o código
  do PR #5. Nome e CPF ou CNPJ quando o Nicolas mandar, e a hospedagem quando for escolhida.
- **Hospedagem e domínio**: perto do lançamento, prepara no papel o monitoramento, a cópia de segurança do
  histórico e o aviso de falha, com custo em reais. Depois da escolha do Nicolas: deploy, Client Secret no
  servidor, DNS, Redirect URI e logo nova no OrzyApp. A recomendação está em
  `/mnt/project-files/orzy/hospedagem-recomendacao.md`. Nada pago, de DNS ou de mudança no app sem o ok dele.
- **Página inicial do site**: entregou a página, que já está no PR #5. Thread encerrada.

Com o Nicolas: a linha "Ficha técnica: X de Y campos" numa rodada do programa do PC (fecha a fase 2); nome e CPF
ou CNPJ para os textos legais, quando quiser; 3 a 5 vendedores pequenos para o beta; e, perto do lançamento, a
hospedagem, a mudança no app do Mercado Livre e o advogado.

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

Ordem decidida pelo Nicolas em 15/10/2026: primeiro o **site base**, funcionando; depois aprimorar até um site
realmente bonito, com a identidade visual (logo, cores e letras) da thread "Identidade visual e logo". O visual
de agora, inclusive o da página inicial, é só uma base, nada perto do modelo final: não vale gastar tempo polindo.

Em 15/10/2026 o Nicolas mandou o Plano de Desenvolvimento 1.0 (ERP, IA proativa e Mercado Livre) e disse que é "só
um plano inicial": serve de referência, não de regra. Ele aprovou a nova ordem depois do site: fase 4 alertas
automáticos e Orzy Intelligence, fase 5 ERP básico (custos e margem), fase 6 executar mudanças com aprovação e
fase 7 Shopee (era a fase 4). A fase 3 ganhou busca e filtro na tabela de anúncios, cuidados antes de abrir ao
público e contagens no beta. Texto do plano e comparação em `/mnt/project-files/orzy/plano/`.

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
  - `/privacidade` e `/termos` mostram os textos de `docs/legal/`, com links e o e-mail de contato
    (orzy.suporte@gmail.com) no rodapé de todas as páginas;
  - o resultado mostra a data e a hora em que os dados foram buscados (termos do Mercado Livre, item 5.3);
  - o histórico com mais de 365 dias é apagado todo dia, e não só quando o servidor liga;
  - descrição da página para o Google e o WhatsApp, `robots.txt` que deixa os robôs só nas páginas públicas,
    resposta a `HEAD` (verificadores de link) e cor dos links com contraste suficiente para leitura;
  - segurança: quem abre o login e não volta perde a sessão em 15 minutos (no máximo 1000 sessões assim; sai a
    mais antiga), o código da sessão muda depois do login e uma conexão parada fecha em 60 segundos;
  - páginas internas conferidas no celular: um apelido ou título sem espaço não empurra mais a página para o lado;
  - comparação de relatórios: cada relatório do histórico mostra o que mudou desde o anterior da mesma conta e do
    mesmo período (situação, visitas, vendas e título de cada anúncio, os novos e os que saíram), sem dizer por
    quê, e a página do resultado leva até ela;
  - histórico no Firestore, para o Cloud Run (`ORZY_HISTORICO=firestore`), testado contra um Firestore simulado;
    o SQLite continua no PC e no Render;
  - um erro inesperado (o histórico fora do ar, por exemplo) mostra uma página de erro, em vez de cortar a conexão;
  - busca pelo título (sem diferença de acento nem de maiúscula, palavras em qualquer ordem) e filtro por situação
    na tabela "Todos os anúncios", no resultado e no histórico;
  - recomendação de hospedagem com custos em reais (thread "Hospedagem e domínio").

## O que foi testado (com dados simulados)

- Programa do PC: login com e sem PKCE, Client Secret escondido ao colar, renovação do login, erros 429, sem internet,
  rede com bloqueio, sem permissão, relatórios de 30 a 150 dias, até 1000 e mais de 1000 anúncios (modo scan),
  CSV aberto no Excel, conta sem anúncios, nota de qualidade com regras pendentes, aviso e ainda não calculada,
  pedido de fotos com outro nome de regra, ordem dos anúncios e limites de chamadas.
- Site (fase 3): login inteiro (estado do OAuth, PKCE, retorno), token que não é gravado em disco, relatório
  com título que tem HTML (sai escapado), CSV com BOM, isolamento entre contas, token vencido sem renovação
  escondida, pedido de outro site recusado, um relatório por vez em cada conexão, histórico com confirmação para
  apagar, cabeçalhos de segurança, uma ida e volta por HTTP real, página inicial com e sem login, textos legais
  lidos de `docs/legal/` (com escape), rodapé com os dois textos e o e-mail, data do relatório em horário de
  Brasília, limpeza diária do histórico que continua depois de um erro, `HEAD` sem corpo, `robots.txt`, descrição
  para buscadores, sessão sem login que some em 15 minutos e o limite delas, código novo da sessão depois do login,
  conexão parada que fecha sem erro e comparação com o relatório anterior do mesmo período (nunca de outra conta
  nem de outro período, com escape dos títulos antigos).
- Histórico no Firestore, contra um Firestore simulado: os mesmos testes do SQLite (cada conta só vê o próprio,
  ordem, prazo de 365 dias, relatório anterior), o prazo para o TTL, o token do servidor de metadados reaproveitado
  e pedido de novo perto de vencer (ou sem resposta), dois relatórios no mesmo instante, apagar em lotes, o
  Firestore fora do ar (o relatório sai mesmo assim, e a página do histórico mostra um erro claro) e as páginas do
  histórico e da comparação com ele.
- Busca e filtro: acento, maiúscula, palavras em qualquer ordem, situação desconhecida (não filtra), texto buscado
  que volta escapado, no resultado e no histórico (SQLite e Firestore).
- No navegador (Chromium), com login e relatórios simulados: as páginas internas (formulário, andamento, resultado
  e histórico) de 320 a 1280 px, nos dois temas, sem nada empurrando a página para o lado. O formulário de busca
  usado de verdade: o endereço guarda a busca, a página volta rolada até a tabela e "Ver todos" mostra a lista
  inteira.
- Testes rodados no Python 3.10 e 3.13 (126: 64 do PC e 62 do site). Quebrar de propósito a checagem do estado do
  OAuth, o escape (de títulos e dos textos legais), o rodapé, a hora de Brasília, a limpeza diária, o `HEAD`, o
  `robots.txt`, o prazo e o limite das sessões sem login, o código novo depois do login, o tempo máximo de uma
  conexão, a escolha do relatório anterior, o escape dos títulos antigos, a página de erro ou, no Firestore, a
  conta, o período, o prazo do TTL, o token, os lotes de apagar ou a ordem do resumo, ou a busca (acento,
  maiúscula, ordem das palavras, situação, escape) faz os testes falharem.

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
3. Site: os passos que o Nicolas aprovou em 15/10/2026 estão prontos (segurança, páginas internas no celular,
   comparação de relatórios e histórico no Firestore), e a busca e o filtro também. Próximos, pela divisão de
   15/10/2026: a logo e as cores da Anel no site base quando a thread da marca avisar, as contagens do beta e,
   depois, o visual final que o Nicolas aprovar. A hospedagem e o que vem com ela (monitoramento e cópia de
   segurança) ficam para perto de lançar.

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
