# 07 · Fase 3: site no orzy.com.br (plano)

**Atualizado em:** 15/10/2026
**Situação:** construindo o site, com o código em rascunho (PR aberto, sem merge). Nada foi contratado, publicado nem
mexido no app do Mercado Livre. Decisão do Nicolas (15/10/2026): o site só vai ao ar quando estiver quase pronto
("só vai pro ar quando estiver 95% concluído"), e não num endereço temporário. As decisões dele estão no fim.

**Quem faz o quê:** ver [06-status.md](06-status.md). Este arquivo cobre o código e as decisões. Os textos legais
estão em [docs/legal/](legal/LEIA-ME.md). A recomendação de hospedagem, com custos, está em
`/mnt/project-files/orzy/hospedagem-recomendacao.md`, e a pesquisa anterior em `/mnt/project-files/orzy/hospedagem-e-lgpd.md`.

## O que o site faz na primeira versão

- Página inicial que explica o Orzy. É uma base (primeiro protótipo, aprovado em 15/10/2026), nada perto do
  visual final.
- O vendedor clica em **Conectar com Mercado Livre** e entra com a própria conta. Ninguém cria app.
- O Client Secret do app fica só no servidor, numa variável de ambiente.
- Gera o relatório em segundo plano, com página de andamento. Quem fechar a página pode voltar depois.
- Mostra o resultado no navegador (o que mudar em cada anúncio primeiro) e baixa o mesmo CSV do PC. A página diz a
  data e a hora em que os dados foram buscados, como pedem os termos do Mercado Livre (item 5.3).
- Guarda um histórico dos relatórios, para abrir cada um depois. Dá para apagar tudo com um clique.
- Compara cada relatório do histórico com o anterior da mesma conta e do mesmo período: o que mudou em cada
  anúncio (situação, visitas, vendas e título), os novos e os que saíram. Diz o que mudou, sem afirmar a causa
  ([03-decisoes-tecnicas.md](03-decisoes-tecnicas.md)). Fotos e ficha técnica não entram: o histórico não as
  guarda, e guardá-las pede mudar a Política de Privacidade.
- Mostra a Política de Privacidade e os Termos de Uso de `docs/legal/` (rascunhos), com os dois e o e-mail de contato
  no rodapé de todas as páginas e o aviso de aceite junto de cada botão Conectar. Tem cabeçalhos de segurança.
- Para buscadores: descrição da página (o resumo que o Google e o WhatsApp mostram) e `robots.txt`, que deixa os
  robôs só nas páginas públicas, para não ligarem o servidor à toa.

Fica de fora (ver o [02-roadmap.md](02-roadmap.md)): alertas automáticos e a Orzy Intelligence (fase 4), custos e
margem (fase 5), alterar anúncios (fase 6), Shopee (fase 7), cobrança e cadastro com senha (o login é só pelo
Mercado Livre). As sugestões do relatório são regras fixas: o site não as chama de IA nem de inteligência artificial.

## Plano em 5 passos (espera o ok do Nicolas)

1. **Construir o site (agora):** primeiro o site base, funcionando (código, páginas, textos legais, segurança e
   histórico); depois aprimorar até um site realmente bonito, com a identidade visual (logo, cores e letras) da
   thread "Identidade visual e logo". Ordem decidida pelo Nicolas em 15/10/2026.
2. **Hospedagem:** escolher uma opção da tabela de custos abaixo e adaptar o código a ela.
3. **App do Mercado Livre:** cadastrar a Redirect URI do site, gerar o Client Secret que vai só para o servidor e
   revisar os campos do formulário (quantos usuários, propósito). Isso muda o app, então só com o ok.
4. **Lançar:** com os textos legais preenchidos (e revisados por advogado, se ele quiser), testar primeiro com a
   conta do Nicolas e um anúncio, no endereço escolhido (o do próprio servidor no beta fechado, ou o orzy.com.br).
5. **Beta fechado:** 3 a 5 vendedores convidados, acompanhar erros; só depois aberto ao público.

## O que já está no código (PR de rascunho)

- `web/`: configuração, sessões na memória, login com PKCE, relatórios em segundo plano, histórico em SQLite ou
  no Firestore, páginas, textos legais, rotas e servidor (só biblioteca padrão do Python).
- `painel-ml/`: a mesma coleta e as mesmas regras do PC. O que mudou para o site: o login passou a ter uma
  versão que não grava em arquivo, e a coleta ganhou etapas e andamento que o PC também usa.
  O PC continua igual: os 64 testes antigos passam sem mudança.
- `testes/firestore_simulado.py`: Firestore e servidor de metadados do Google simulados, para testar o histórico
  no Firestore sem conta e sem internet.
- `testes/test_site.py`: 63 testes contra o Mercado Livre e o Firestore simulados. Cobrem o login inteiro, o
  estado do OAuth, o escape de títulos, o CSV com BOM, o isolamento entre contas, token vencido, pedido de outro
  site, histórico, cabeçalhos de segurança, uma ida e volta por HTTP real (com `HEAD`), a página inicial, os textos
  legais (com escape), o rodapé, a hora do relatório em horário de Brasília, a limpeza diária do histórico, o
  `robots.txt`, a descrição para buscadores, as sessões sem login (prazo e limite), o código novo da sessão depois
  do login, a conexão parada, a palavra sem espaço que quebra no celular, a comparação com o relatório anterior,
  a busca e o filtro da tabela, a logo, os ícones e a fonte da marca e o histórico no Firestore (os mesmos testes
  do SQLite, mais token, prazo para o TTL e Firestore fora do ar).
- Verificado: 127 testes passam no Python 3.13 e no 3.10 (64 do PC e 63 do site); pyflakes limpo. Quebrar de
  propósito a checagem do estado, o escape (de títulos e dos textos legais), o rodapé, a hora de Brasília, a
  limpeza diária, o `HEAD`, o `robots.txt`, o prazo e o limite das sessões sem login, o código novo depois do
  login, o tempo máximo de uma conexão, a escolha do relatório anterior, o escape dos títulos antigos, a página
  de erro, a busca (acento, maiúscula, ordem das palavras, situação, escape) ou, no Firestore, a conta, o
  período, o prazo do TTL, o token, os lotes de apagar ou a ordem do resumo faz os testes falharem.

Limites da primeira versão (propostos, a confirmar):
- **Uma instância só**: as sessões e os relatórios em andamento ficam na memória do servidor.
- **Até 300 anúncios por relatório**, com aviso na tela quando passa disso.
- **Dois relatórios ao mesmo tempo** no servidor inteiro, e um por vez em cada conexão (sessão).
- **Histórico apagado após 365 dias** (o servidor confere ao ligar e depois uma vez por dia).
- **Sem refresh token**: quando o login vence (6 horas), a pessoa entra de novo.
- **Sessões sem login** (quem clicou em Conectar e não voltou do Mercado Livre) somem em 15 minutos, no máximo
  1000 de uma vez. Quem entra ganha um código de sessão novo, e uma conexão parada fecha em 60 segundos.

Conferido no navegador (Chromium), com login e relatórios simulados: as páginas internas (formulário, andamento,
resultado e histórico) de 320 a 1280 px, nos dois temas. Nada empurra a página para o lado, e as tabelas largas
rolam dentro da própria caixa. O formulário de busca foi usado de verdade: o endereço guarda a busca, a página
volta rolada até a tabela e "Ver todos" mostra a lista inteira. Só funcionamento: o visual final vem depois,
com a identidade escolhida.

Não testado ainda: o site falando com o Mercado Livre de verdade (depende da Redirect URI cadastrada, passo 3),
o Firestore de verdade (só o simulado), HTTPS e domínio e carga com muitos anúncios.

## Custos de hospedagem (estimativas de 15/10/2026)

Câmbio de referência: US$ 1 = R$ 5,04 (cotação de 14/10/2026, 10h45, renovainvest.com.br). Os preços mudam:
conferir na hora de contratar. Nada foi contratado.

| Opção | Estimativa (R$/mês) | Prós | Contras |
|---|---|---|---|
| **Google: Cloud Run + Firestore em São Paulo** (recomendação da thread "Hospedagem e domínio") | R$ 0 no teste (até 55 horas de servidor ligado no mês); até R$ 0,42 por hora além disso; teto de cerca de R$ 276. Mais a porta de entrada: R$ 0 (A ou B) ou cerca de R$ 92 (C) | O servidor só liga quando alguém usa; servidor e histórico no Brasil; o contrato do Google Cloud já traz as cláusulas da ANPD | Exige o plano Blaze (cartão); o código precisa das mudanças da seção abaixo |
| **Render**, plano pago de entrada (US$ 7/mês, 512 MB de RAM) + disco persistente (US$ 0,25/GB/mês) | cerca de R$ 37 (com 1 GB de disco) | Roda o código quase como está; o Client Secret fica no painel do serviço | Cobra desde o primeiro mês; sem região no Brasil; o contrato não fala de LGPD, então só a região de Frankfurt (União Europeia) evita as cláusulas da ANPD |
| **Hostinger VPS KVM 1** (1 vCPU, 4 GB, 50 GB) | cerca de R$ 35 (promoção de US$ 6,99 no 1º ano) a R$ 98 (preço cheio de US$ 19,49) | Sempre ligado; controle total | Alguém precisa cuidar do Linux (atualizações, cópia de segurança); datacenter no Brasil não confirmado |
| **Railway**, plano Hobby (US$ 5/mês + uso de CPU e RAM) | estimativa de R$ 35 a R$ 100, conforme o uso real | Deploy simples; disco (volume) persistente | Cobra pelo uso: difícil prever o mês |

**Recomendação (thread "Hospedagem e domínio"):** o servidor no Cloud Run e o histórico no Firestore, os dois em São
Paulo, porque o teste sai de graça e o contrato do Google Cloud cobre a LGPD. O Render é a alternativa se ele preferir
um valor fixo e o código quase sem mudança. A escolha fica para a hora de lançar.

A porta de entrada (quem recebe as visitas) também fica para a hora de lançar:
- **A. Endereço do próprio Cloud Run** (`....run.app`): R$ 0, coberto pelo contrato. Serve para o beta fechado.
- **B. Firebase Hosting no orzy.com.br** (onde está a página temporária): R$ 0, mas fica fora das cláusulas da ANPD.
  Só com o ok de um advogado.
- **C. Balanceador de carga do Google no orzy.com.br:** cerca de R$ 92/mês, coberto pelo contrato.

## Se a hospedagem for o Google: o que muda no código

Da recomendação da thread de hospedagem. Entra quando o Nicolas escolher a hospedagem, não antes, menos o item 1,
que ele aprovou em 15/10/2026.

1. **Histórico no Firestore** (A, B e C): o disco do Cloud Run apaga a cada reinício. Pronto no PR #5
   (`web/historico_firestore.py`, ligado com `ORZY_HISTORICO=firestore` e `ORZY_FIRESTORE_PROJETO`), testado contra
   um Firestore simulado. Na hora de publicar: criar o banco no modo nativo em São Paulo, dar à conta de serviço do
   Cloud Run o papel Cloud Datastore User (`roles/datastore.user`) e ligar a política de TTL no campo `expira_em`
   da coleção `relatorios` (o passo a passo está em `web/LEIA-ME.md`).
2. **Cookie `__session`** (só na B): o Firebase apaga qualquer outro cookie antes de repassar o pedido ao servidor.
3. **Páginas públicas como arquivos** (só na B): início, privacidade, termos e `robots.txt` saem direto do Firebase,
   sem ligar o servidor. Hoje a página inicial muda com o login (mostra "Ver meu relatório" a quem já entrou):
   como arquivo, mostraria sempre "Conectar". Decidir na hora se isso basta.
4. **Sessão some depois de 15 minutos sem uso** (A, B e C): o servidor desliga, e quem estava conectado conecta de
   novo. Os relatórios salvos continuam no histórico.

## Mercado Livre: o que o app precisa

1. **Redirect URI:** incluir a do site (`https://orzy.com.br/retorno`, ou a do endereço escolhido para o beta) e
   manter a do PC (`https://www.google.com`).
2. **Client Secret:** o Mercado Livre tem um só por app. Gerar um novo invalida o atual, então o PC precisa rodar
   `python conectar.py --refazer` de novo (com o segredo novo). O segredo do site fica só no painel de hospedagem.
   Isso segue a decisão de 14/10: um app só, o "OrzyApp".
3. **Quantos usuários e propósito:** a documentação não diz o efeito de cada resposta. Confirmar antes de abrir
   para vendedores de fora (a validar).
4. **Conta dona do app:** a pessoal do Nicolas serve para começar. Antes do público, vale avaliar uma conta de empresa
   (a validar na documentação).
5. **Termos para desenvolvedores:** lidos em 15/10/2026 pela thread "Privacidade e termos" (resumo em
   [docs/legal/LEIA-ME.md](legal/LEIA-ME.md)). Não fixam prazo para guardar dados; pedem finalidade, segurança e
   apagar as cópias que não servem mais. O histórico de 12 meses, privado e que o vendedor apaga quando quiser, é
   compatível na leitura mais razoável (confirmar com advogado). O item 5.3 pede dados atualizados a cada 24 horas e
   que o aplicativo diga quando atualizou: por isso o resultado e o histórico mostram a data de cada relatório.

## LGPD (resumo, não é parecer jurídico)

Texto da Resolução CD/ANPD nº 2/2022, lido em 15/10/2026:
- Agente de pequeno porte (ME, EPP, MEI, startup ou pessoa natural com fins econômicos) fica dispensado de
  indicar encarregado, mas precisa manter um canal de comunicação com quem tem os dados.
- Pode usar o registro de operações simplificado.
- Os prazos de atendimento e de comunicação de incidentes são dobrados, sem número fixo no texto: depende de
  norma específica da ANPD (a confirmar com advogado).
- O site não trata dados sensíveis. Por isso, em princípio, não cai no regime de alto risco. Confirmar.

O que o site guarda: o número e o apelido do vendedor (durante a sessão), e o histórico com títulos e números
dos anúncios. Tokens: só na memória. Dados de compradores: nenhum.

Dados fora do Brasil: a transferência precisa das cláusulas-padrão da ANPD no contrato (o do Google Cloud tem; o do
Render e o do Firebase Hosting não) ou de um país que a ANPD reconhece como adequado (a União Europeia, pela Resolução
CD/ANPD nº 32/2026).

Antes de abrir ao público: Política de Privacidade e Termos de Uso preenchidos (rascunhos em `docs/legal/`, que o
site mostra em `/privacidade` e `/termos`), canal de contato, responsável identificado, e uma conversa com advogado.
Não tenho preço confiável de advogado: pedir orçamento.

## Decisões que o Nicolas precisa tomar

Nenhuma é urgente: todas ficam para quando o site estiver quase pronto.

1. Hospedagem: Google, com Cloud Run e Firestore em São Paulo (recomendado: R$ 0 no teste, teto de cerca de R$ 276/mês,
   plano Blaze com cartão), ou Render (cerca de R$ 37/mês fixos). Com o Google, também a porta de entrada: A, B ou C.
2. Aprovar o passo 3 (mudança no app do Mercado Livre e novo Client Secret, com o PC rodando `--refazer`).
3. Limites da primeira versão: 300 anúncios por relatório, histórico por 12 meses, uma instância.
4. Nome e contato do responsável e um e-mail de contato para a Política de Privacidade e os Termos.
5. Quando: beta fechado com 3 a 5 vendedores, ou direto ao público.
6. Revisão de advogado antes do público: sim ou não.

## Próximo passo

- Nicolas: nada agora. As decisões acima ficam para quando o site estiver quase pronto.
- Site (thread "Site: código e login"): terminar o site base, nos passos aprovados em 15/10/2026 (segurança,
  páginas internas no celular, comparação de relatórios e histórico no Firestore). Depois, o visual final com a
  identidade que o Nicolas escolher. As mudanças da hospedagem entram quando ela for escolhida.
- Hospedagem e domínio: parada até o lançamento. Nada de DNS, cobrança ou mudança no app sem o ok dele.
- Privacidade e termos: preencher os campos marcados quando o Nicolas mandar os dados.
