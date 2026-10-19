# 06 · Status

**Atualizado em:** 19/10/2026
**Fase atual:** 4. Os passos 1 e 2 estão prontos (PR #12 e PR #13): o site passou para Django com PostgreSQL em
`sistema/`, com o visual novo, e a conta é criada no Conectar, com o acesso ao Mercado Livre guardado com criptografia.
Próximo: o passo 3 (importação completa), com o ok do Nicolas.
As fases 2 e 3 (site base) estão concluídas. Pela ordem aprovada em 18/10/2026, nada vai ao ar antes de o sistema
inteiro funcionar (fase 10). Plano em `/mnt/project-files/orzy/plano/nova-ordem-sistema-completo.md`.

## Quem faz o quê (15/10/2026, nova divisão)

Dividido de novo a pedido do Nicolas em 15/10/2026 (texto completo em
`/mnt/project-files/orzy/plano/divisao-das-tarefas.md`). Duas frentes não mexem nos mesmos arquivos ao mesmo
tempo, e poucas ficam ativas de cada vez, porque cada thread ativa gasta o limite de uso do plano do Nicolas.

Agora:

- **Site: código e login**: a fase 4. O passo 1 está pronto (PR #12, 19/10/2026): o sistema em Django com
  PostgreSQL, em `sistema/`, com o visual novo de `/mnt/project-files/orzy/marca/visual-final/`. O passo 2 também
  (PR #13, 19/10/2026): a conta, o acesso guardado com criptografia, a página "Sua conta" e o "Desconectar e apagar
  tudo". Próximo: o passo 3, importação completa, depois do ok do Nicolas. Arquivos: `sistema/`, `testes/`, `painel-ml/`,
  `requirements.txt`, `docs/01` a `docs/07` (menos `docs/legal/`) e o README.
- **Identidade visual e logo**: em 17/10/2026 o Nicolas escolheu o layout Lima, com fundo escuro, e em 18/10/2026 a
  thread entregou o pacote em `/mnt/project-files/orzy/marca/visual-final/` (as páginas públicas prontas e modelos
  das telas do sistema, conferidos com a regra de segurança do site), que já está no `sistema/`. Não mexe no código:
  o visual entra pela thread do site. Depois desenha as telas do ERP no mesmo visual, fase a fase, e segue ajustando
  o visual com o Nicolas.

Esperando:

- **Privacidade e termos**: `docs/legal/` (PR #6, #7, #8 e #9, mesclados em 15/10/2026); o site mostra esses
  textos em `/privacidade` e `/termos`. A thread conferiu a Política e os Termos contra o site base do PR #5
  (PR #10, mesclado em 15/10/2026), e os dois ajustes que ela pediu no código estão no PR #5: a sessão com login
  acaba 8 horas depois do login, mesmo em uso, e as contagens do beta são apagadas depois de 12 meses. Nome e CPF
  ou CNPJ quando o Nicolas mandar, e a hospedagem quando for escolhida. Na fase 4, recebe as mudanças da Política e
  dos Termos para a conta guardada (passo 2, pronto: o que mudou e as frases que ficaram velhas estão em
  `/mnt/project-files/orzy/sistema/passo-2-conta-e-acesso.md`), os dados importados (passo 3) e a IA. Até a Política
  mudar, ninguém além do Nicolas usa o sistema. O passo 1 não mudou o que fica guardado, mas as referências ao código em `docs/legal/LEIA-ME.md` apontam para o `web/`, que saiu: a lista com os
  arquivos do `sistema/` está em `/mnt/project-files/orzy/sistema/referencias-da-politica-no-codigo.md`.
- **Hospedagem e domínio**: refaz o plano para o sistema completo (PostgreSQL num plano grátis até o lançamento,
  tarefas em segundo plano para a importação e a sincronia, e-mail dos alertas) e traz o custo do endereço de teste
  do fim da fase 4 para o ok do Nicolas. No lançamento: monitoramento, cópia de segurança, deploy, Client Secret no
  servidor, DNS, Redirect URI e logo nova no OrzyApp. A recomendação de hoje está em
  `/mnt/project-files/orzy/hospedagem-recomendacao.md`. Nada pago, de DNS ou de mudança no app sem o ok dele.
- **Página inicial do site**: entregou a página, que já está no PR #5. Thread encerrada.

Com o Nicolas (seção 5 do plano da nova ordem): a linha "Ficha técnica: X de Y campos" numa rodada do programa do PC
(fecha a fase 2); no fim da fase 4, o ok no endereço de teste (cartão no plano Blaze do Google e o endereço no
OrzyApp) e a conta na API da Anthropic, com crédito pré-pago e limite de gasto; antes da fase 8, rever os preços dos
planos; no começo da fase 8, a conta de desenvolvedor no Mercado Pago; nome e CPF ou CNPJ antes de outra pessoa usar
com dados de verdade; e, antes do lançamento, o advogado, o CNPJ e o contador, a porta de entrada do orzy.com.br e o
ID da conta dele no Mercado Livre (o que o `conectar.py` mostra).

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

Em 16/10/2026 o Nicolas definiu o objetivo: "um sistema erp COMPLETO junto com a integração de uma ia que faz a
análise dos dados", e pediu que, ao criar a conta, um botão leve ao Mercado Livre e o Orzy puxe tudo (anúncios,
fotos, estoque, vendas e visitas). Em 17/10/2026 ele aprovou um novo roadmap, que substitui a ordem acima: fase 4
conta, importação completa e Orzy Intelligence, começando com a troca para Django e PostgreSQL; fase 5 empresa,
produtos, custos e margem; fase 6 pedidos, estoque e compras; fase 7 financeiro; fase 8 mudanças no Mercado Livre com
aprovação (era a 6); fase 9 Shopee e multicanal (era a 7); e fase 10 nota fiscal, por um emissor que já existe.
Proposta em `/mnt/project-files/orzy/plano/erp-completo-proposta.md`.

Em 17/10/2026 (19:32 UTC) o Nicolas mudou a ordem: o site só vai ao ar quando o painel, a integração com o Mercado
Livre, o pagamento, a assinatura e a IA estiverem funcionando; antes, ele testa e dá uma conta demo para o professor
dele. Em 18/10/2026 ele aprovou a nova ordem, sem beta com vendedores convidados ("Sem convidados"): fases 4 a 7 como
acima, fase 8 planos, assinatura e pagamento, fase 9 testes completos (os dele e a demo do professor) e fase 10 o
lançamento. Mudanças no Mercado Livre, Shopee e nota fiscal ficam para depois do lançamento. O PR #5 entra no main
como base da fase 4, e o visual novo vai direto para o sistema novo. Plano em
`/mnt/project-files/orzy/plano/nova-ordem-sistema-completo.md`.

Em 19/10/2026 ficou pronto o passo 1 da fase 4 (PR #12, com o "pode seguir" do Nicolas): o site do PR #5 passou
para Django com PostgreSQL, em `sistema/`, já com o visual novo, e o `web/` saiu. O banco guarda o mesmo que o site
base guardava (o histórico e as contagens), e o que a Política promete continua valendo: o acesso ao Mercado Livre
só na memória, um cookie só, a sessão de no máximo 8 horas e o histórico de 12 meses. Nada foi publicado.

No mesmo dia ficou pronto o passo 2 (PR #13, com outro "pode seguir" do Nicolas): a conta é criada no clique em
Conectar, sem senha, e o código que renova o acesso ao Mercado Livre (o refresh token) vai para o banco cifrado, com a
chave fora dele. A página "Sua conta" mostra o que fica guardado e tem o "Desconectar e apagar tudo", que também tira
a permissão do Orzy no Mercado Livre. Escolhas feitas no lugar do Nicolas, que ele pode mudar: quando o Mercado Livre
recusa o acesso (permissão tirada ou senha trocada, que dão o mesmo erro), o acesso sai na hora e a conta com o
histórico espera 30 dias por um novo Conectar. Isso muda o que a Política promete (o acesso só na memória): até a
thread "Privacidade e termos" atualizar o texto, com o ok do Nicolas, ninguém além dele usa o sistema. Nada foi
publicado.

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
- Fase 3, site base (PR #5, mesclado em 18/10/2026 como base da fase 4):
  - `web/`: o site (login com PKCE, relatório em segundo plano, histórico, páginas e servidor, só biblioteca padrão);
  - `painel-ml/`: o login e a coleta ganharam versões que o site usa sem gravar em arquivo; o PC continua igual;
  - `testes/test_site.py`: testes do site contra o Mercado Livre simulado;
  - `docs/07-fase-3-plano.md`: plano em 5 passos, custos em reais, LGPD e decisões que faltam;
  - página inicial (aprovada como primeiro protótipo em 15/10/2026), com o aviso de aceite dos Termos junto de cada
    botão Conectar;
  - `/privacidade` e `/termos` mostram os textos de `docs/legal/`, com links e o e-mail de contato
    (orzy.suporte@gmail.com) no rodapé de todas as páginas;
  - o resultado mostra a data e a hora em que os dados foram buscados (termos do Mercado Livre, item 5.3);
  - o histórico e as contagens do beta com mais de 365 dias são apagados todo dia, e não só quando o servidor liga;
  - descrição da página para o Google e o WhatsApp, `robots.txt` que deixa os robôs só nas páginas públicas,
    resposta a `HEAD` (verificadores de link) e cor dos links com contraste suficiente para leitura;
  - segurança: quem abre o login e não volta perde a sessão em 15 minutos (no máximo 1000 sessões assim; sai a
    mais antiga), o código da sessão muda depois do login e uma conexão parada fecha em 60 segundos;
  - a sessão com login acaba 8 horas depois do login, mesmo em uso, e o servidor apaga as vencidas a cada minuto,
    mesmo sem ninguém usando o site: a Política promete tirar o login da memória até 8 horas depois da entrada;
  - páginas internas conferidas no celular: um apelido ou título sem espaço não empurra mais a página para o lado;
  - comparação de relatórios: cada relatório do histórico mostra o que mudou desde o anterior da mesma conta e do
    mesmo período (situação, visitas, vendas e título de cada anúncio, os novos e os que saíram), sem dizer por
    quê, e a página do resultado leva até ela;
  - histórico no Firestore, para o Cloud Run (`ORZY_HISTORICO=firestore`), testado contra um Firestore simulado;
    o SQLite continua no PC e no Render;
  - um erro inesperado (o histórico fora do ar, por exemplo) mostra uma página de erro, em vez de cortar a conexão;
  - busca pelo título (sem diferença de acento nem de maiúscula, palavras em qualquer ordem) e filtro por situação
    na tabela "Todos os anúncios", no resultado e no histórico;
  - marca Anel no site base: a logo no topo (muda com o tema), as cores dos temas claro e escuro, o favicon, o
    ícone do iPhone e a fonte Geist, servida pelo próprio site. A imagem de compartilhamento já está em
    `web/static`; as etiquetas que a mostram no WhatsApp entram no lançamento, com o endereço público;
  - contagens do beta: a página `/contagens`, que só abre para as contas de `ORZY_CONTAS_ADMIN` (a do Nicolas),
    mostra logins, relatórios sem erro e com erro e anúncios lidos por dia, guardados sem dizer de quem, e as
    contas com relatório guardado e os anúncios por conta, tirados do histórico na hora em que a página abre. As
    contagens com mais de 12 meses são apagadas, como o histórico;
  - recomendação de hospedagem com custos em reais (thread "Hospedagem e domínio").
- Fase 4, passo 1 (PR #12, 19/10/2026):
  - `sistema/`: o sistema em Django 6.1 com PostgreSQL 16. Faz o que o site base fazia: login com PKCE, sessões só
    na memória, relatório em segundo plano, histórico com a comparação, busca e filtro, contagens do beta e os
    textos legais de `docs/legal/`, com as mesmas regras e a mesma coleta do PC;
  - o visual novo: as páginas públicas do pacote (início, textos legais e erro, iguais ao pacote fora de
    comentários e espaços) e as telas do sistema montadas com os modelos dele (formulário, andamento com o anel,
    resultado com os números e o que pede atenção, histórico com a linha do tempo e a comparação, contagens);
  - o rodapé com os textos legais e o e-mail de contato em todas as telas do sistema (o modelo não tinha);
  - páginas e arquivos de `/static/` comprimidos (menos tráfego até o Brasil, que a hospedagem cobra por GiB), e os
    arquivos com o resumo do conteúdo no nome, que o navegador guarda até mudarem;
  - todo pedido conferido com o endereço do site (os outros recebem 400);
  - `sistema/gunicorn.conf.py`: o servidor da hospedagem com um processo só e uma linha de registro por pedido,
    sem IP e sem a busca do endereço;
  - `requirements.txt` com Django, psycopg, gunicorn e WhiteNoise; o programa do PC continua sem nada para instalar;
  - o GitHub roda os testes do sistema a cada PR, com um PostgreSQL só para o teste;
  - saíram `web/`, `testes/test_site.py` e `testes/firestore_simulado.py`: sem o beta, o Firestore não é usado.
- Fase 4, passo 2 (PR #13, 19/10/2026):
  - `sistema/contas/models.py`: a tabela das contas (número e apelido no Mercado Livre, quando entrou, o último
    Conectar e o acesso guardado cifrado). Os relatórios guardados passam a ser da conta e saem com ela pelo próprio
    banco; os que já existiam ganham uma conta sem acesso guardado (migração `0002`);
  - `sistema/contas/cofre.py`: a cifra AES-256-GCM (biblioteca `cryptography`), com a chave em `ORZY_CHAVE_ACESSO`;
  - `sistema/contas/acesso.py`: guardar no Conectar, renovar um de cada vez com o código novo salvo antes, perder o
    acesso quando o Mercado Livre recusa (as sessões da conta acabam em todos os navegadores), a conferência de todo
    dia, as contas sem acesso há 30 dias e o "Desconectar e apagar tudo";
  - a página "Sua conta" (`/conta`), aberta pelo círculo com as iniciais no topo, e a página de conta apagada;
  - o relatório renova o login sozinho quando o token de acesso vence (6 horas), em vez de pedir um novo Conectar;
  - `painel-ml/ml_api.py` ganhou `tirar_permissao`, que o programa do PC não usa, e o Mercado Livre simulado ganhou
    o `DELETE` da permissão.
- Depois do passo 2 (19/10/2026), com as respostas da thread "Privacidade e termos" (em `docs/legal/LEIA-ME.md`):
  - a frase da página inicial diz que quem apaga tudo, na hora, é o "Desconectar e apagar tudo", na página Sua conta;
  - `python manage.py apagar_conta <número da conta>` faz o mesmo que o botão, para quem pede por e-mail;
  - no `sistema/LEIA-ME.md` ("Antes de publicar"), a linha à parte de quando a pessoa apaga vale para os dois botões
    e para o comando, guardada pelo prazo das cópias de segurança do banco mais 1 dia;
  - Testes: 112 do sistema (eram 109), com o comando (pergunta antes, não apaga sem o número certo, apaga mesmo sem
    a confirmação do Mercado Livre) e a frase nova da página inicial.

## O que foi testado (com dados simulados)

- Programa do PC: login com e sem PKCE, Client Secret escondido ao colar, renovação do login, erros 429, sem internet,
  rede com bloqueio, sem permissão, relatórios de 30 a 150 dias, até 1000 e mais de 1000 anúncios (modo scan),
  CSV aberto no Excel, conta sem anúncios, nota de qualidade com regras pendentes, aviso e ainda não calculada,
  pedido de fotos com outro nome de regra, ordem dos anúncios e limites de chamadas.
- Site (fase 3): login inteiro (estado do OAuth, PKCE, retorno), token que não é gravado em disco, relatório com
  título que tem HTML (sai escapado), CSV com BOM, isolamento entre contas, token vencido sem renovação escondida,
  pedido de outro site recusado, um relatório por vez em cada conexão, histórico com confirmação para apagar,
  cabeçalhos de segurança, uma ida e volta por HTTP real, página inicial com e sem login, textos legais lidos de
  `docs/legal/` (com escape), rodapé com os dois textos e o e-mail, data do relatório em horário de Brasília, limpeza
  diária do histórico que continua depois de um erro, `HEAD` sem corpo, `robots.txt`, descrição para buscadores,
  sessão com login que acaba 8 horas depois do login (mesmo usada a cada hora) e a limpeza das sessões a cada minuto,
  sessão sem login que some em 15 minutos e o limite delas, código novo da sessão depois do login, conexão parada que
  fecha sem erro e comparação com o relatório anterior do mesmo período (nunca de outra conta nem de outro período,
  com escape dos títulos antigos).
- Histórico no Firestore, contra um Firestore simulado: os mesmos testes do SQLite (cada conta só vê o próprio,
  ordem, prazo de 365 dias, relatório anterior), o prazo para o TTL, o token do servidor de metadados reaproveitado
  e pedido de novo perto de vencer (ou sem resposta), dois relatórios no mesmo instante, apagar em lotes, o
  Firestore fora do ar (o relatório sai mesmo assim, e a página do histórico mostra um erro claro) e as páginas do
  histórico e da comparação com ele.
- Busca e filtro: acento, maiúscula, palavras em qualquer ordem, situação desconhecida (não filtra), texto buscado
  que volta escapado, no resultado e no histórico (SQLite e Firestore).
- Contagens do beta, no SQLite e no Firestore simulado: login, relatório sem erro (também o de conta sem anúncios),
  erro do Mercado Livre e erro inesperado contados; login que não terminou não conta; uma contagem que falha não
  atrapalha o login nem o relatório; a página só abre para as contas de `ORZY_CONTAS_ADMIN` e não mostra conta,
  apelido nem anúncio; o Firestore soma no próprio servidor, sem apagar as outras contagens do dia; e os dias com
  mais de 365 dias são apagados, contados pelo dia de Brasília.
- No navegador (Chromium), com login e relatórios simulados: as páginas internas (formulário, andamento, resultado,
  histórico e contagens) de 320 a 1280 px, nos dois temas, sem nada empurrando a página para o lado. O formulário
  de busca usado de verdade: o endereço guarda a busca, a página volta rolada até a tabela e "Ver todos" mostra a
  lista inteira.
- Sistema (fase 4, passo 1), 87 testes contra o Mercado Livre simulado e um PostgreSQL de teste. Os do site base
  que continuam valendo: login inteiro (estado e PKCE), token só na memória e nenhuma tabela de sessão no banco,
  código novo da sessão depois do login, sessão que acaba 8 horas depois do login, sessões sem login com prazo e
  limite, limpezas a cada minuto e todo dia, escape, CSV com BOM, isolamento entre contas, token vencido, pedido de
  outro site, um relatório por vez, histórico, comparação, busca e filtro, contagens e a página só para quem pode,
  textos legais com escape, rodapé, cabeçalhos de segurança, `robots.txt`, `HEAD` e a página inicial com e sem
  login. E os novos: os campos de cada tabela iguais aos da Política, contagens somadas por 4 pedidos ao mesmo tempo,
  arquivos de `/static/` com o resumo no nome e comprimidos, páginas comprimidas, nenhuma página com estilo ou
  script escrito dentro do HTML, pedido com outro endereço recusado e o andamento do relatório.
- No navegador (Chromium), com login e relatórios simulados: as páginas públicas e todas as telas do sistema, de 320
  a 1280 px, sem nada empurrando a página para o lado. O gunicorn ligado com a configuração do sistema: um processo,
  as limpezas no mesmo processo e o registro sem IP e sem a busca.
- Sistema (fase 4, passo 2), 109 testes: a cifra (abre só com a mesma chave e na mesma conta, não abre mexida, e
  cada vez sai diferente), o Conectar que cria a conta e o Conectar de novo que atualiza a mesma, o login sem o
  código de renovação, a conta que não salva (o login não conclui), o código de renovação e o token de acesso que não
  aparecem abertos em nenhuma tabela, 4 renovações ao mesmo tempo sem nenhuma recusada, o código novo salvo antes de
  o token sair, o token vencido ou recusado que renova sozinho, a permissão tirada (o acesso sai, as sessões da conta
  acabam em todos os navegadores, o histórico fica e o Conectar de novo volta), o erro passageiro e a chave trocada
  que não apagam nada, a conferência de todo dia (renova só quem não renovou e percebe quem tirou a permissão), as
  contas sem acesso há 30 dias (com o histórico, pelo banco), a página "Sua conta", o "Desconectar e apagar tudo"
  (pede confirmação e o código do formulário, apaga só a conta certa, encerra as sessões e tira a permissão, também
  sem o token da sessão, e apaga mesmo quando o Mercado Livre não confirma) e as páginas sem login.
- Testes rodados no passo 2: 173 (64 do PC, no Python 3.10 e no 3.13, e 109 do sistema, no 3.13 com o PostgreSQL
  16). Quebrar de propósito 31 pontos faz os testes falharem, entre eles: a trava da renovação, salvar o código novo,
  o erro que apaga o acesso, as sessões que acabam junto, a conta na conferência da cifra, a chave conferida, o
  Conectar de novo, a conferência de todo dia, o prazo de 30 dias, o apagar pelo banco, o tirar a permissão e a
  confirmação para apagar.
- Testes rodados no passo 1: 151 (64 do PC, no Python 3.10 e no 3.13, e 87 do sistema, no 3.13 com o PostgreSQL 16).
  Quebrar de propósito 11 pontos do sistema faz os testes falharem: o código de renovação descartado, o prazo de 8 horas, o
  escape dos títulos, quem abre `/contagens`, o relatório guardado de outra conta, a confirmação para apagar, o
  código novo depois do login, as etapas do andamento, a compressão, o dia das contagens apagadas e a conferência
  do endereço.
- Site base (fase 3), testes rodados no Python 3.10 e 3.13 (148: 64 do PC e 84 do site). Quebrar de propósito a
  checagem do estado do OAuth, o escape (de títulos e dos textos legais), o rodapé, a hora de Brasília, a limpeza
  diária, o `HEAD`, o `robots.txt`, o prazo da sessão com login contado do login, a limpeza das sessões a cada minuto,
  o prazo e o limite das sessões sem login, o código novo depois do login, o tempo máximo de uma conexão, a escolha do
  relatório anterior, o escape dos títulos antigos, a página de erro ou, no Firestore, a conta, o período, o prazo do
  TTL, o token, os lotes de apagar ou a ordem do resumo, a busca (acento, maiúscula, ordem das palavras, situação,
  escape) ou as contagens do beta (o que conta, o dia de Brasília, somar em vez de trocar, o último relatório de cada
  conta, quem abre a página, apagar os dias antigos) faz os testes falharem.

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
- [ ] O login do site com o Mercado Livre de verdade (no endereço de teste, no fim da fase 4, com a Redirect URI dele
  no app).
- [ ] A renovação pelo acesso guardado e o "Desconectar e apagar tudo" com o Mercado Livre de verdade (no mesmo
  endereço de teste).

## Próximo passo

1. Nicolas: nada urgente agora. O que ele providencia e quando está na seção 5 de
   `/mnt/project-files/orzy/plano/nova-ordem-sistema-completo.md`; a primeira coisa é o ok no endereço de teste, no
   fim da fase 4.
2. Nicolas: quando puder, baixar o ZIP de novo do GitHub. Para não fazer login de novo, copiar o `config.json` e o
   `tokens.json` da pasta `painel-ml` usada por último para a nova. Rodar `python meus_anuncios.py` e mandar o
   texto do que apareceu no cmd (sem print). Ver a linha "Ficha técnica: X de Y campos".
3. Sistema: os passos 1 e 2 da fase 4 estão prontos (PR #12 e PR #13). Próximo: o passo 3 (importação completa:
   anúncios de todos os status, fotos só pelos links, estoque, 12 meses de vendas sem dados do comprador e 150 dias
   de visitas), com o ok do Nicolas. O endereço de teste entra no fim da fase 4, com o ok dele; a hospedagem do
   lançamento e o que vem com ela (monitoramento e cópia de segurança) ficam para a fase 10.

Na conversa, mandar só o texto do que apareceu no cmd, sem print. **Nunca** mandar o Client Secret,
o `config.json`, o `tokens.json` nem o banco do site.

## Em aberto

- Conta com mais anúncios para conferir: sem vendedores convidados (18/10/2026), ficam a loja de teste do Mercado
  Livre e, se ele quiser, a conta do professor.
- O que "propósito" e "quantos usuários" do formulário do app mudam: a documentação do Mercado Livre não fala.
- Hospedagem do sistema completo: a thread "Hospedagem e domínio" refaz o plano (Cloud Run em São Paulo e um banco
  PostgreSQL num plano grátis até o lançamento). A porta de entrada do orzy.com.br decide na hora de lançar; o
  Firebase Hosting fica fora das cláusulas da ANPD.
- Termos do Mercado Livre para desenvolvedores (lidos em 15/10/2026): não fixam prazo para guardar dados. O histórico
  de 12 meses, privado e que o vendedor apaga, é compatível na leitura mais razoável; confirmar com advogado.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
