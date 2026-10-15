# 07 · Fase 3: site no orzy.com.br (plano)

**Atualizado em:** 15/10/2026
**Situação:** construindo o site, com o código em rascunho (PR aberto, sem merge). Nada foi contratado, publicado nem
mexido no app do Mercado Livre. Decisão do Nicolas (15/10/2026): o site só vai ao ar quando estiver quase pronto
("só vai pro ar quando estiver 95% concluído"), e não num endereço temporário. As decisões dele estão no fim.

**Quem faz o quê:** ver [06-status.md](06-status.md). Este arquivo cobre o código e as decisões. Os textos legais
estão em [docs/legal/](legal/LEIA-ME.md). A recomendação de hospedagem, com custos, está em
`/mnt/project-files/orzy/hospedagem-recomendacao.md`, e a pesquisa anterior em `/mnt/project-files/orzy/hospedagem-e-lgpd.md`.

## O que o site faz na primeira versão

- Página inicial que explica o Orzy, aprovada pelo Nicolas como primeiro protótipo (logo e cores vêm depois).
- O vendedor clica em **Conectar com Mercado Livre** e entra com a própria conta. Ninguém cria app.
- O Client Secret do app fica só no servidor, numa variável de ambiente.
- Gera o relatório em segundo plano, com página de andamento. Quem fechar a página pode voltar depois.
- Mostra o resultado no navegador (o que mudar em cada anúncio primeiro) e baixa o mesmo CSV do PC. A página diz a
  data e a hora em que os dados foram buscados, como pedem os termos do Mercado Livre (item 5.3).
- Guarda um histórico dos relatórios, para abrir cada um depois. Dá para apagar tudo com um clique.
- Mostra a Política de Privacidade e os Termos de Uso de `docs/legal/` (rascunhos), com os dois no rodapé de todas as
  páginas e o aviso de aceite junto de cada botão Conectar. Tem cabeçalhos de segurança.
- Para buscadores: descrição da página (o resumo que o Google e o WhatsApp mostram) e `robots.txt`, que deixa os
  robôs só nas páginas públicas, para não ligarem o servidor à toa.

Fica de fora: alterar anúncios, IA, Shopee, cobrança e cadastro com senha (o login é só pelo Mercado Livre).

## Plano em 5 passos (espera o ok do Nicolas)

1. **Construir o site (agora):** código, página inicial, textos legais e, depois, a identidade visual (logo e cores).
2. **Hospedagem:** escolher uma opção da tabela de custos abaixo e adaptar o código a ela.
3. **App do Mercado Livre:** cadastrar a Redirect URI do site, gerar o Client Secret que vai só para o servidor e
   revisar os campos do formulário (quantos usuários, propósito). Isso muda o app, então só com o ok.
4. **Lançar:** com os textos legais preenchidos (e revisados por advogado, se ele quiser), testar primeiro com a
   conta do Nicolas e um anúncio, no endereço escolhido (o do próprio servidor no beta fechado, ou o orzy.com.br).
5. **Beta fechado:** 3 a 5 vendedores convidados, acompanhar erros; só depois aberto ao público.

## O que já está no código (PR de rascunho)

- `web/`: configuração, sessões na memória, login com PKCE, relatórios em segundo plano, histórico em SQLite,
  páginas, textos legais, rotas e servidor (só biblioteca padrão do Python).
- `painel-ml/`: a mesma coleta e as mesmas regras do PC. O que mudou para o site: o login passou a ter uma
  versão que não grava em arquivo, e a coleta ganhou etapas e andamento que o PC também usa.
  O PC continua igual: os 64 testes antigos passam sem mudança.
- `testes/test_site.py`: 32 testes contra o Mercado Livre simulado. Cobrem o login inteiro, o estado do OAuth,
  o escape de títulos, o CSV com BOM, o isolamento entre contas, token vencido, pedido de outro site, histórico,
  cabeçalhos de segurança, uma ida e volta por HTTP real (com `HEAD`), a página inicial, os textos legais (com
  escape), o rodapé, a hora do relatório em horário de Brasília, a limpeza diária do histórico, o `robots.txt` e
  a descrição para buscadores.
- Verificado: 96 testes passam no Python 3.13 e no 3.10 (64 do PC e 32 do site); pyflakes limpo. Quebrar de
  propósito a checagem do estado, o escape (de títulos e dos textos legais), o rodapé, a hora de Brasília, a
  limpeza diária, o `HEAD` ou o `robots.txt` faz os testes falharem.

Limites da primeira versão (propostos, a confirmar):
- **Uma instância só**: as sessões e os relatórios em andamento ficam na memória do servidor.
- **Até 300 anúncios por relatório**, com aviso na tela quando passa disso.
- **Dois relatórios ao mesmo tempo** no servidor inteiro, e um por vez em cada conexão (sessão).
- **Histórico apagado após 365 dias** (o servidor confere ao ligar e depois uma vez por dia).
- **Sem refresh token**: quando o login vence (6 horas), a pessoa entra de novo.

Não testado ainda: o site falando com o Mercado Livre de verdade (depende da Redirect URI cadastrada, passo 3),
HTTPS e domínio, carga com muitos anúncios e as páginas internas no celular (a página inicial foi conferida de
360 a 1280 px).

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

Da recomendação da thread de hospedagem. Entra quando o Nicolas escolher a hospedagem, não antes.

1. **Histórico no Firestore** (A, B e C): o disco do Cloud Run apaga a cada reinício. A thread de hospedagem pode
   entregar o módulo (só biblioteca padrão, com testes).
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
- Site (thread "Site: código e login"): seguir construindo o que não depende de decisão. As mudanças da hospedagem
  entram quando ela for escolhida, e a identidade visual quando o Nicolas trouxer logo e cores.
- Hospedagem e domínio: parada até o lançamento. Nada de DNS, cobrança ou mudança no app sem o ok dele.
- Privacidade e termos: preencher os campos marcados quando o Nicolas mandar os dados.
