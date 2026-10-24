# Privacidade e termos do Orzy

**Situação (19/10/2026):** rascunhos, escritos pelo Claude a partir do código. Nada está publicado.
Não é parecer jurídico: antes de abrir o site ao público, o ideal é um advogado revisar.

| Arquivo | O que é |
|---|---|
| [politica-de-privacidade.md](politica-de-privacidade.md) | Quais dados o site usa, para que, por quanto tempo e os direitos do vendedor (LGPD) |
| [termos-de-uso.md](termos-de-uso.md) | As regras de uso do site: o que ele faz, o que não faz, responsabilidades e lei aplicável |

Os textos descrevem o sistema da fase 4 até o passo 2 (`sistema/`, main em `b2c82e8`, conferido em 19/10/2026): a
conta e o acesso ao Mercado Livre guardado, cifrado. O que mudou nos textos está em "O que o passo 2 mudou nos
textos", abaixo. Este rascunho espera o passo 3 (a importação completa), que muda os textos de novo, e vai ao Nicolas
numa revisão só. Até a Política mudar no main, ninguém além do Nicolas usa o sistema. Se o código mudar nos pontos da
tabela "De onde vem cada frase", os textos mudam junto.

Para achar o que falta, procure por `[PREENCHER` (só o Nicolas sabe) e `[CONFIRMAR` (depende de outra frente).

**Como o site mostra os textos:** as páginas `/privacidade` e `/termos` leem os dois arquivos desta pasta a cada
visita (`sistema/publico/legal.py`). O site entende só parte do Markdown: títulos, parágrafos, listas de um nível (a
continuação de um item vai recuada), citações (`>`), tabelas, negrito, código e links. Não use itálico, lista dentro de
lista, linha horizontal nem imagem, e não comece uma linha de parágrafo com `- `, `* `, `|`, `>`, `# ` ou um número
seguido de ponto e espaço, porque ela vira outra coisa. O que vem antes do primeiro `##` é a cabeça da página: o
título, o aviso (a primeira citação), a linha `**Versão:**` e a abertura. Cada `##` entra no índice da página. Nos `##`
e `###`, o número do começo vira um selo e o título ganha um endereço próprio (por exemplo,
`/privacidade#8-os-seus-direitos`): mudar o número ou o nome de um item muda o endereço. `[PREENCHER: ...]` e
`[CONFIRMAR: ...]` aparecem marcados na página. Os links para `politica-de-privacidade.md` e `termos-de-uso.md` viram
`/privacidade` e `/termos`; outros links relativos, como o deste LEIA-ME, aparecem como texto. Os testes do sistema
abrem as duas páginas com os textos desta pasta (`sistema/testes/test_paginas.py`).

## O que só o Nicolas preenche

| Campo | Onde aparece | Observação |
|---|---|---|
| Nome completo do responsável, ou nome da empresa | Política (item 1) e Termos (início) | É quem responde pelos dados perante a lei. Precisa ser maior de 18 anos (ou emancipado), ou uma empresa. |
| CPF ou CNPJ | Política (item 1) e Termos (início) | Enquanto o Orzy for grátis, a LGPD pede a identificação do responsável; publicar o CPF não parece obrigatório (confirmar com advogado). Quando cobrar, o Decreto nº 7.962/2013 exige CPF ou CNPJ e endereço no site. |
| Data de publicação | Os dois | Muda a cada versão. |

Já perguntado no thread "Site: código e login": se haverá revisão de advogado antes do público.

## O que depende das outras frentes

**Hospedagem e domínio:** o nome da empresa de hospedagem e, se o banco de dados for de outra empresa, o nome dela
também (Política, item 4), o país dos servidores e do banco (item 5) e por quanto tempo elas guardam registros de
acesso e cópias de segurança (itens 2.4 e 6). O banco é um PostgreSQL num plano grátis até o lançamento, escolhido pela
thread de hospedagem no fim da fase 4; o contrato de dados dele (LGPD) passa por esta thread antes de entrar dado de
outra pessoa. Texto do item 5 para cada caso:

- **Brasil:** "Os dados ficam em servidores no Brasil."
- **União Europeia (ex.: Frankfurt):** "Os dados ficam em servidores na Alemanha, na União Europeia. A ANPD reconhece
  que a União Europeia protege dados pessoais em nível adequado (Resolução CD/ANPD nº 32/2026)."
- **Estados Unidos ou outro país:** "Os dados ficam em servidores em [país]. Essa transferência segue as
  cláusulas-padrão contratuais aprovadas pela ANPD (Resolução CD/ANPD nº 19/2024), que fazem parte do contrato com a
  hospedagem." Só vale se o contrato da hospedagem tiver mesmo essas cláusulas: desde 23/08/2025 elas são exigidas
  para quem usa esse caminho. O contrato de dados do Render (DPA de 19/12/2024) não fala de LGPD nem da ANPD e diz
  que o processamento principal é nos Estados Unidos. O Render não tem servidor no Brasil (tem Oregon, Ohio, Virgínia,
  Frankfurt e Singapura). Em qualquer transferência para fora do Brasil, a Política também precisa dizer a finalidade,
  a duração e os direitos ligados a ela, e o Orzy entrega o texto das cláusulas a quem pedir (Resolução CD/ANPD
  nº 19/2024).
- **Google (recomendação da thread de hospedagem, 15/10/2026, ainda não decidida):** plano feito para o site base, com
  o histórico no Firestore. O sistema da fase 4 usa PostgreSQL, e a thread de hospedagem refaz o plano no fim da fase 4:
  o que vale para o servidor continua, o que vale para o banco muda. Servidor no Cloud Run e histórico no Firestore, os
  dois em São Paulo, contratados com a Google Cloud Brasil Computação e Serviços de Dados Ltda.
  Segundo a thread de hospedagem, Cloud Run, Firestore, Secret Manager e Cloud Logging seguem o Cloud Data Processing
  Addendum do Google Cloud, que traz as cláusulas-padrão da ANPD na parte "Brazil". O que recebe as visitas muda a
  conta. O endereço do próprio Cloud Run (`...run.app`, grátis, bom para um teste fechado) e um balanceador de carga do
  Google no orzy.com.br (cerca de R$ 92 por mês) ficam cobertos por esse contrato. O Firebase Hosting, que serve hoje a
  página temporária do orzy.com.br, segue outro contrato: os Firebase Data Processing and Security Terms (21/08/2024),
  que não falam de LGPD nem da ANPD. Ele guarda o IP de quem visita "por alguns meses", e com ele o servidor iria para
  os Estados Unidos. Com o Firebase Hosting na frente, a transferência desses IPs fica sem base clara no art. 33 da
  LGPD: o consentimento não cobre quem só abre a página inicial, e "necessário para o contrato" é fraco para esse uso.
  Então ele só serve com o ok de um advogado. Ligar o domínio direto no Cloud Run não resolve, porque é um recurso em
  teste, e nenhum contrato de dados do Google vale para ele.
- **Se for Google, mudam também nos textos** (plano de monitoramento da thread de hospedagem, 16/10/2026, em
  `/mnt/project-files/orzy/hospedagem-monitoramento.md`): os registros de pedidos do Cloud Run, que guardariam o IP, o
  endereço com a busca e o `?code=` e o navegador, ficam de fora. Então, no item 2.4, a frase dos registros da
  hospedagem passa a dizer que o Google recebe o endereço IP para entregar as páginas, mas o Orzy não guarda IP, o
  endereço com a busca nem o navegador; a frase dos registros do servidor fica como está. No item 6, os registros do
  servidor ficam 30 dias num depósito em São Paulo, e o histórico e as contagens ganham uma cópia de segurança por dia,
  guardada 7 dias em São Paulo (era o Firestore; com o PostgreSQL, vale o que o banco escolhido fizer): um dado apagado
  pode ficar até 7 dias nas cópias, e depois o Google conclui a exclusão em até 180 dias. Um robô abre `/saude` a cada
  5 minutos, então o servidor não desliga quando ninguém usa o site, e a sessão dura até **Sair** ou 8 horas depois do
  login, como a Política já diz (ela ainda acaba se o servidor reiniciar). Na cobrança por pedido, o padrão do Cloud
  Run, a CPU só funciona durante algum pedido, e as tarefas em segundo plano (a limpeza das sessões e, desde o passo 2,
  a renovação dos acessos) andam com os pedidos do robô; para as 8 horas valerem, a thread do código faz a limpeza na
  nuvem apagar as sessões 6 minutos antes do prazo, no lançamento. Os avisos de erro por e-mail ao responsável não
  trazem dado de vendedor; se um dia trouxerem, a Política precisa contar. Só com o Firebase Hosting, o cookie passa a
  se chamar `__session`.
- **Registro de quem apagou** (proposta da thread de hospedagem, aceita por esta thread em 16/10/2026 e ampliada em
  19/10/2026): quando alguém usa **Apagar meu histórico** ou **Desconectar e apagar tudo**, ou quando o responsável
  apaga uma conta a pedido, por e-mail (o comando `apagar_conta`), o número da conta, a hora e o que foi apagado ficam
  num registro à parte, fora do banco e fora do registro comum do servidor, só para apagar de novo se for preciso
  voltar uma cópia de segurança do banco. Sem ele, voltar uma cópia traria de volta o que a pessoa apagou, até o acesso
  guardado de quem desconectou. O prazo é o das cópias do banco mais 1 dia (8 dias com as cópias de 7 dias do plano de
  16/10/2026). Fora do banco porque voltar uma cópia apagaria um registro guardado nele. Quando o código fizer isso,
  entram na Política uma frase no item 2.4, uma linha no item 3 (cumprimento de obrigação legal: garantir a eliminação
  pedida, arts. 7º, II, e 18, VI) e uma linha no item 6. A thread do site anotou isso para antes do endereço de teste
  (`sistema/LEIA-ME.md`, "Antes de publicar").

**Site: código e login:** os itens da seção seguinte.

**Página inicial:** link para a Política e os Termos no rodapé e a frase "Não somos o Mercado Livre". Sem o logotipo
do Mercado Livre (os termos deles só permitem as marcas conforme o manual de marcas do Mercado Livre) e sem ferramenta
de estatística (Google Analytics e parecidos) ou outros cookies. Se entrar alguma, a Política precisa mudar antes. Na
parte de segurança, desde 19/10/2026 (PR #16), a frase diz "Na página Sua conta, “Desconectar e apagar tudo” apaga
tudo na hora" (`sistema/publico/templates/publico/inicio.html:407`, conferida em `sistema/testes/test_paginas.py:106`
e `107`). Antes, ela dizia que o **Apagar meu histórico** apagava tudo.

**Nicolas, na conta dele:** o caminho do menu do Mercado Livre onde o vendedor tira a permissão de um aplicativo
(Política, item 8). A documentação para desenvolvedores não diz.

## O que o site precisa ter para os textos valerem

Já feito no sistema (main, `b2c82e8`):

1. Páginas `/privacidade` e `/termos`, que mostram os arquivos desta pasta.
2. Junto de cada botão **Conectar com Mercado Livre**: "Ao conectar, você aceita os Termos de Uso e confirma que leu a
   Política de Privacidade", com os dois links. Não há caixa de marcar: o Nicolas aprovou a página inicial assim, e dá
   para pôr uma depois, se um advogado preferir.
3. Links para os dois textos no rodapé de todas as páginas.
4. Na página do resultado, a data e a hora em que os dados foram buscados; no histórico, o aviso de que cada relatório
   mostra os anúncios como estavam naquele dia. Os termos do Mercado Livre (5.3) pedem que o aplicativo diga com que
   frequência os dados são atualizados, e os Termos (item 6) prometem isso.
5. Relatórios e contagens do beta com mais de 12 meses apagados ao ligar o servidor e depois a cada 24 horas.
6. O e-mail de contato em todas as páginas: no rodapé, ou no texto da página de erro.
7. Sessão sem login (de quem clicou em Conectar e não voltou do Mercado Livre) apagada depois de 15 minutos, com no
   máximo 1000 de uma vez, e código novo da sessão depois do login.
8. Contagens do beta só em números por dia, e a página `/contagens` só para as contas de `ORZY_CONTAS_ADMIN`, sem
   mostrar de quem são os números. Com poucos vendedores no beta, um dia pode apontar para uma pessoa se for cruzado com
   o histórico (o único login do dia, por exemplo), e a LGPD só deixa de valer para dados que não dá para ligar de volta
   à pessoa com esforço razoável (art. 12). Por isso a Política conta que as contagens existem, dá a base legal
   (legítimo interesse) e promete 12 meses (item 6).
9. Sessão com login apagada do servidor no máximo 8 horas depois do login, mesmo que a pessoa continue usando o site: o
   prazo conta da hora do login, e o servidor confere a cada minuto, mesmo sem visitas, e apaga um minuto antes do prazo
   (no Cloud Run, ver "Se for Google" acima). O cookie vence no mesmo prazo.
10. A conta e o acesso guardado (passo 2): o código de renovação vai para o banco cifrado com AES-256-GCM, com o número
    da conta na conferência da cifra, e a chave fica numa variável de ambiente obrigatória (`ORZY_CHAVE_ACESSO`),
    nunca no banco. O token de acesso continua só na memória, na sessão.
11. A página **Sua conta** mostra o que fica guardado e tem o **Desconectar e apagar tudo**: apaga a conta, o acesso e o
    histórico, encerra as sessões da conta em todos os navegadores e pede ao Mercado Livre para tirar a permissão do
    Orzy. Se o Mercado Livre não confirmar, o Orzy apaga do lado dele mesmo assim e a página diz para tirar por lá.
12. Quando o Mercado Livre recusa o acesso guardado (permissão tirada ou senha trocada, que dão o mesmo erro), o acesso
    sai na hora e as sessões da conta acabam; a conta e o histórico saem 30 dias depois, sem um novo Conectar. A
    conferência de todo dia renova quem não renovou nas últimas 20 horas, então entre duas renovações passam no máximo
    44 horas: é o tempo máximo para o Orzy perceber, com o servidor ligado.
13. **Sair** encerra só a sessão daquele navegador, e **Apagar meu histórico** apaga só os relatórios: nos dois, a conta
    e o acesso guardado ficam.
14. Pedido para apagar por e-mail: `python manage.py apagar_conta <número da conta>` apaga como o **Desconectar e
    apagar tudo** e diz se o Mercado Livre confirmou que tirou a permissão. Ele roda fora do servidor, e as sessões
    ficam na memória do servidor: uma sessão aberta da conta continua até **Sair**, até 8 horas depois do login ou até
    o servidor reiniciar. Ela não guarda mais nada da conta: sem a conta, o relatório não vai para o histórico.

Regras que continuam valendo:

- Antes de guardar um dado novo, pedir e-mail, pôr cookies ou estatística, usar IA ou mudar a hospedagem de país,
  atualizar a Política.
- `ORZY_HORAS_SESSAO` muda o prazo da sessão e do cookie (padrão: 8 horas). Mais de 8 só depois de mudar a Política
  (itens 2.4 e 6), que promete 8.
- O prazo de 30 dias depois de o acesso parar de valer (`DIAS_SEM_ACESSO`, `sistema/contas/acesso.py:30`) aparece na
  página Sua conta, na Política (itens 3, 6 e 8) e nos Termos (item 4). Se o número mudar, os textos mudam junto.
- Se o responsável virar empresa (CNPJ): guardar data, hora e IP de cada acesso por 6 meses, em sigilo (Marco Civil
  da Internet, art. 15). Hoje o site não guarda IP.

## O que o passo 2 mudou nos textos

Para a revisão do Nicolas e do advogado. Antes, o Orzy não guardava o acesso: ele ficava só na memória, durante a
sessão.

Política de Privacidade:

- **Resumo:** o acesso guardado cifrado e renovado sozinho; o **Desconectar e apagar tudo**; o Orzy não altera nada na
  conta, a não ser tirar a própria permissão quando a pessoa pede.
- **2.1:** a conta no Orzy, criada no primeiro **Conectar**; o código de renovação guardado cifrado; a renovação no
  meio do uso e mais ou menos uma vez por dia, que não lê os dados.
- **2.4:** o registro do servidor não anota o IP.
- **3:** guardar e renovar o acesso e manter a conta por 30 dias quando o Mercado Livre recusa o acesso, como
  execução do contrato.
- **4 e 5:** a hospedagem do site e o banco de dados em linhas separadas, cada um com o seu país.
- **6:** os prazos do código de renovação e da conta; o histórico sai junto com a conta; as cópias de segurança são as
  do banco.
- **7:** a cifra (AES-256-GCM) e a chave só no ambiente do servidor, fora do código e do banco.
- **8:** **Desconectar e apagar tudo**, **Apagar meu histórico** (só os relatórios) e **Sair** (só a sessão); quem
  tira a permissão no Mercado Livre perde o acesso guardado quando o Orzy percebe, em até dois dias, e a conta e o
  histórico 30 dias depois, não mais em 12 meses.

Termos de Uso:

- **4:** a conta no Orzy e o acesso guardado e renovado; a sessão de 8 horas; o que acontece quando o Mercado Livre
  recusa o acesso; o **Desconectar e apagar tudo**.
- **11 e 12:** para parar de usar, o **Desconectar e apagar tudo**; para quem não concordar com uma versão nova, o
  mesmo botão antes de ela valer, ou o pedido por e-mail.

## Decisões desta thread (19/10/2026)

Sobre os pontos que a thread do site deixou para esta thread nos passos 1 e 2 da fase 4:

- **Registro do servidor sem IP:** cada linha do gunicorn tem data e hora, método, página sem a busca, resposta,
  tamanho e tempo, sem o IP. A Política (item 2.4) diz que o servidor não anota o endereço IP. As linhas dos pedidos
  com outro endereço (robôs) mostram só o endereço recusado, nada do vendedor, e não pedem frase.
- **Banco de dados de outra empresa:** o item 4 da Política tem a hospedagem do site e o banco de dados em linhas
  separadas, cada uma com o seu `[PREENCHER]` (podem ser a mesma empresa), e o item 5 pede o país dos dois.
- **Registro de quem apagou:** continua, agora também para o **Desconectar e apagar tudo** e o comando `apagar_conta`
  (ver "Registro de quem apagou", acima). As limpezas automáticas (12 meses, e 30 dias sem acesso) não precisam dele:
  depois de voltar uma cópia, elas apagam de novo sozinhas, porque a regra está nos próprios dados (no máximo, os 30
  dias recomeçam).
- **30 dias depois de o Mercado Livre recusar o acesso:** aceito. Os termos do Mercado Livre (2.2.4) pedem para
  revogar o acesso aos dados de quem avisou o desenvolvedor que não vai mais usar o aplicativo, e o **Desconectar e
  apagar tudo** faz isso na hora; o item 14 trata do Mercado Livre cortar o acesso do desenvolvedor. Quem tira a
  permissão pelo Mercado Livre perde o acesso guardado assim que o Orzy percebe, e a espera curta, dita na Política,
  protege quem só trocou a senha. Quem quiser antes conecta de novo e usa o **Desconectar e apagar tudo**, ou escreve
  para o e-mail.
- **Sessão aberta no pedido por e-mail:** fica como está. A Política só promete encerrar as sessões no **Desconectar
  e apagar tudo** e quando o Mercado Livre recusa o acesso (item 8), e o item 6 já diz que o número, o apelido e o
  código de acesso ficam na sessão até ela acabar. A resposta ao e-mail não promete que a sessão acabou.
- **Sugestão para o passo 3 (não decidida):** hoje a conta que continua com acesso, mas não é usada, fica guardada sem
  prazo (o histórico sai em 12 meses). Com a importação e a sincronia do passo 3, o Orzy leria todo dia a conta de quem
  parou de usar. Sugestão: a conta sem nenhum Conectar há 12 meses sai com tudo, como o histórico. Quem decide é o
  Nicolas, com a thread do site.

## O que o Mercado Livre exige

Lido em 15/10/2026 nos [termos para desenvolvedores](https://developers.mercadolibre.com.ar/en_us/mercado-libre-developer-terms-and-conditions)
(a página em inglês; não tem data de versão), e os itens 2.2.4 e 14 relidos em 19/10/2026:

| Item dos termos | O que pede | Como o Orzy cumpre |
|---|---|---|
| 6 | Cumprir a LGPD; usar os dados só para a finalidade; o usuário do Mercado Livre que autoriza é o controlador e o desenvolvedor segue as instruções dele; subcontratados com a mesma segurança; avisar o Mercado Livre se uma autoridade pedir dados | Política itens 2.3, 3 e 4. Avisar o Mercado Livre fica com o responsável, se acontecer |
| 10 | Medidas de segurança para dados pessoais (nomes, e-mails), credenciais e apelidos | Política item 7; o acesso guardado vai cifrado, com a chave fora do banco |
| 2.2.1.3 | Cópias intermediárias só as necessárias, apagadas de vez quando não servem mais | Token de acesso só na memória; código de renovação só enquanto a conta está conectada, cifrado; cadastro e compradores descartados na hora |
| 2.2.4 | Revogar o acesso do aplicativo aos dados de quem avisou o desenvolvedor que não vai mais usar; não usar "mercado", "libre", "livre", "payment", "shipments" nem "credit" no nome ou no visual do aplicativo | **Desconectar e apagar tudo** apaga a conta, o acesso e o histórico e pede ao Mercado Livre para tirar a permissão; por e-mail, o responsável faz o mesmo com o comando `apagar_conta` (ver "Antes de abrir ao público"); o nome Orzy está fora da lista |
| 4.1 | Deixar sempre claro que o aplicativo não pertence ao Mercado Livre; marcas do Mercado Livre só conforme o manual de marcas deles | Termos item 2 e rodapé do site |
| 5.2 e 5.3 | Informação não pública do usuário só com autorização dele; conteúdo atualizado pelo menos a cada 24 horas; o aplicativo informa a frequência de atualização | Termos item 6 e site item 4 acima |
| 2.2.2 | Client Secret em sigilo; avisar o Mercado Livre se houver uso indevido | Secret só no ambiente do servidor |
| 7.9 | Não guardar dados de cartão nem números de documento sem autorização | O Orzy não guarda |
| 9 | O Mercado Livre pode auditar e suspender o acesso por suspeita de falha de segurança | Termos item 2 |
| 14 | Se o Mercado Livre cortar o acesso do desenvolvedor: parar de usar a API e destruir as cópias e os dados pessoais obtidos | Apagar todas as contas nesse caso: o acesso guardado e o histórico saem junto |
| 17 | Os termos podem mudar; a mudança vale 10 dias depois de publicada | Reler antes de abrir ao público |

**Histórico de 12 meses (pergunta do thread do site):** os termos não fixam prazo para guardar dados; pedem
finalidade, segurança e apagar cópias que não servem mais. Um histórico privado, do próprio vendedor, que ele apaga
quando quiser, é compatível na leitura mais razoável. O ponto de atenção é o item 5.3 (atualização a cada 24 horas),
porque o histórico mostra títulos antigos; como ele é privado e mostra a data de cada relatório, o risco parece baixo.
Confirmar com advogado.

**O que o Mercado Livre não exige:** nem a documentação nem o formulário do aplicativo (visto em 14/10/2026) pedem
link de política de privacidade, e o aplicativo não precisa de certificação. A certificação (Developer Partner
Program) é opcional e pede, entre outras coisas, que os vendedores que usam o aplicativo faturem pelo menos
US$ 2,5 milhões por mês no Brasil, e uma avaliação de segurança. "Aplicativo não certificado" na lista de aplicativos
é o normal.

## O que a LGPD pede e onde está

| Exigência | Onde está |
|---|---|
| Finalidade, forma e duração do tratamento, quem é o responsável e como falar com ele, com quem compartilha, direitos (art. 9º) | Política itens 1 a 8 |
| Base legal para cada uso (art. 7º) | Política item 3 |
| Direitos do titular e resposta em até 15 dias (arts. 18 e 19) | Política item 8 |
| Critérios de decisões automatizadas, quando pedidos (art. 20) | Política itens 2.2 e 8 |
| Transferência internacional com mecanismo válido, dizendo finalidade, duração, país e direitos (art. 33; Resoluções CD/ANPD nº 19/2024 e 32/2026) | Política item 5, conforme a hospedagem |
| Segurança e comunicação de incidentes (arts. 46 e 48; Resolução CD/ANPD nº 15/2024) | Política item 7 |
| Canal de comunicação no lugar do encarregado (Resolução CD/ANPD nº 2/2022, art. 11) | Política item 1 |
| Dado anonimizado só deixa de ser pessoal se não der para voltar à pessoa com esforço razoável (art. 12) | Contagens do beta: Política itens 2.4, 3 e 6 |
| Eliminação quando o tratamento acaba (arts. 15 e 16) | Política itens 6 e 8: a conta e o acesso saem com o **Desconectar e apagar tudo**, ou 30 dias depois de o Mercado Livre recusar o acesso |

O Orzy cabe como **agente de tratamento de pequeno porte** (Resolução CD/ANPD nº 2/2022): pessoa física ou empresa
pequena, sem tratamento de alto risco, porque não usa dados sensíveis nem de crianças, trata poucos vendedores e as
sugestões não decidem nada sobre ninguém. Com isso: não precisa de encarregado, mas precisa do canal (art. 11); pode
usar registro e política de segurança simplificados (arts. 9º e 13); e tem prazo em dobro para atender pedidos e
comunicar incidentes (art. 14). Os textos prometem o prazo normal de 15 dias, que vale para qualquer caso.

## Antes de abrir ao público (fora dos textos)

- Registro simplificado das operações de tratamento (LGPD art. 37; Resolução CD/ANPD nº 2/2022, art. 9º; a ANPD tem
  um modelo).
- Plano para incidente: avisar a ANPD e os vendedores em até 3 dias úteis (6 para agente de pequeno porte) quando houver
  risco ou dano relevante, e guardar o registro de todo incidente por 5 anos (Resolução CD/ANPD nº 15/2024).
- Contrato de dados (LGPD) do banco grátis, antes de entrar dado de outra pessoa: a thread de hospedagem escolhe o
  banco no fim da fase 4.
- **Pedido para apagar tudo por e-mail:** ter um jeito de rodar o comando do item 14 acima na hospedagem, com
  `--no-input`. Na resposta, dizer o que saiu e, se o comando avisar que o Mercado Livre não confirmou, pedir para a
  pessoa tirar a permissão por lá. Não prometer que uma sessão aberta acabou: ela acaba no **Sair** ou até 8 horas
  depois do login. Quem consegue entrar no Orzy pode usar o próprio botão, que também encerra as sessões na hora.
- **E-mail de contato:** orzy.suporte@gmail.com, criado pelo Nicolas em 15/10/2026. É um Gmail comum: segue os termos de
  consumidor do Google, sem contrato de tratamento de dados nem as cláusulas-padrão da ANPD, e as mensagens podem ficar
  em servidores fora do Brasil (a Política diz isso nos itens 4 e 5). O Google diz que pode pôr essas cláusulas nos
  contratos de serviços comerciais, como o Google Workspace, que é pago. Antes de abrir ao público, confirmar com o
  advogado se a transferência das mensagens se apoia no art. 33, IX, da LGPD (necessária para responder a quem
  escreveu); se não, trocar por um e-mail com contrato de dados e ajustar os itens 4 e 5 da Política.
- Ler o e-mail de contato e responder pedidos em até 15 dias; apagar mensagens resolvidas há mais de 12 meses.
- Reler os termos do Mercado Livre e conferir se mudaram.

## De onde vem cada frase

Código do main em `b2c82e8` (fase 4, passo 2, com o comando `apagar_conta`), conferido em 19/10/2026.

| O que os textos dizem | Onde está no código |
|---|---|
| O código de acesso fica só na memória do servidor | `sistema/contas/sessoes.py:1` a `13` e `126` a `181` (o motor de sessão do Django, só na memória); `sistema/orzy/settings.py:71`; `sistema/contas/login.py:63` e `64`; `sistema/contas/views.py:40` |
| De `/users/me` ficam só o número e o apelido | `sistema/contas/login.py:65` a `69` |
| O que o histórico guarda | `sistema/relatorios/models.py:12` a `33`; `sistema/relatorios/historico.py:38` a `53` |
| Histórico e contagens do beta apagados com mais de 12 meses, ao ligar e depois a cada 24 horas | `sistema/relatorios/historico.py:18` e `85` a `92`; `sistema/relatorios/limpezas.py:19` a `35` e `77` a `83`; `sistema/orzy/wsgi.py:17` a `19` |
| O que mudou desde o relatório anterior do mesmo período, sem dizer por quê | `sistema/relatorios/comparacao.py`; `sistema/relatorios/historico.py:69` a `78`; `sistema/relatorios/templates/relatorios/historico_relatorio.html:44` |
| Cookie `orzy_sessao`: HttpOnly, SameSite=Lax, Secure em HTTPS, dura 8 horas | `sistema/orzy/settings.py:72` a `76`; `sistema/orzy/configuracao.py:14`, `29` e `124` |
| Sessão sem login apagada depois de 15 minutos, no máximo 1000 de uma vez; código novo depois do login | `sistema/contas/sessoes.py:22` e `23`, `58` a `69` e `109` a `123`; `sistema/contas/views.py:37` a `39` |
| Sessão com login apagada do servidor no máximo 8 horas depois do login, mesmo em uso, conferida a cada minuto | `sistema/contas/sessoes.py:103` a `123` e `129` a `131`; `sistema/relatorios/limpezas.py:62` a `74`; `sistema/orzy/wsgi.py:19` |
| Até 300 anúncios por relatório | `sistema/orzy/configuracao.py:28` e `123` |
| Um relatório por vez em cada conexão | `sistema/relatorios/geracao.py:120` e `121` |
| O registro do servidor anota só o caminho, sem o código do Mercado Livre, a busca nem o IP | `sistema/gunicorn.conf.py:21` a `24` (o servidor da hospedagem); `sistema/orzy/settings.py:105` a `120` e `sistema/orzy/seguranca.py:21` a `37` (o servidor de teste do computador e os pedidos com outro endereço) |
| Contagens do beta: só números por dia, sem conta, apelido nem anúncio | `sistema/relatorios/contagens.py:13` a `19`; `sistema/relatorios/models.py:36` a `42`; `sistema/relatorios/historico.py:96` a `104`; `sistema/relatorios/geracao.py:162`; `sistema/contas/views.py:36` |
| Página `/contagens` só para as contas de `ORZY_CONTAS_ADMIN`, sem mostrar de quem são os números | `sistema/relatorios/views.py:136` a `143`; `sistema/orzy/configuracao.py:112` a `115` e `125`; `sistema/relatorios/historico.py:113` a `116` |
| O que o relatório lê de cada anúncio | `painel-ml/meus_anuncios.py:28` e `29` |
| Dos pedidos, só o anúncio e a quantidade | `painel-ml/meus_anuncios.py:137` a `165` |
| "Não somos o Mercado Livre", os links para os dois textos e o e-mail de contato | Página inicial: `sistema/publico/templates/publico/inicio.html:454` a `466`. Textos legais: `sistema/publico/templates/publico/legal.html:134` a `146`. Telas do sistema: `sistema/publico/templates/sistema.html:34` a `37`. Na página de erro, o rodapé tem a frase e os dois links, e o e-mail fica no texto da página (`sistema/publico/templates/publico/erro.html:48`, `53` e `54`) |
| Aviso de aceite junto de cada botão Conectar | `sistema/publico/templates/publico/inicio.html:72` e `432` |
| Data e hora em que os dados foram buscados | `sistema/relatorios/geracao.py:67`; `sistema/relatorios/templates/relatorios/resultado.html:12` |
| O histórico mostra como os anúncios estavam no dia | `sistema/relatorios/templates/relatorios/historico_relatorio.html:29` |
| Fonte, ícones e imagens saem do próprio site, sem serviço de fora na página | `sistema/orzy/settings.py:89` a `98` (a regra de segurança da página só aceita o próprio site); os arquivos em `sistema/publico/static/` |
| O site mostra os textos desta pasta | `sistema/orzy/settings.py:102` e `103`; `sistema/orzy/urls.py:11` e `12`; `sistema/publico/legal.py:22` e `37` a `44` |
| A conta: número e apelido no Mercado Livre, o primeiro e o último Conectar, quando o acesso foi salvo e desde quando está sem acesso | `sistema/contas/models.py:13` a `20` |
| A conta é criada ou atualizada no Conectar, com o código de renovação cifrado; o token de acesso fica só na sessão | `sistema/contas/login.py:60` a `69`; `sistema/contas/acesso.py:41` a `62` |
| A cifra: AES-256-GCM, com o número da conta na conferência (o valor de uma conta não abre na linha de outra) | `sistema/contas/cofre.py:39` a `58` |
| A chave fica fora do banco, numa variável de ambiente obrigatória | `sistema/orzy/configuracao.py:13`, `27`, `76` a `86` e `122` |
| Renovar um de cada vez, com o código novo salvo antes de usar | `sistema/contas/acesso.py:65` a `105` |
| O Mercado Livre recusou: o acesso sai na hora e as sessões da conta acabam | `sistema/contas/acesso.py:89` a `104`; `sistema/contas/sessoes.py:97` a `101` |
| A conferência de todo dia renova quem não renovou nas últimas 20 horas | `sistema/contas/acesso.py:31` e `150` a `172`; `sistema/relatorios/limpezas.py:38` a `59` e `77` a `83` |
| A conta sem acesso há 30 dias, e sem Conectar nesse tempo, sai com o histórico | `sistema/contas/acesso.py:30` e `175` a `190` |
| "Desconectar e apagar tudo" | `sistema/contas/views.py:69` a `85`; `sistema/contas/acesso.py:108` a `147`; `painel-ml/ml_api.py:264` a `270` |
| Pedido por e-mail: o comando apaga como o botão e diz se o Mercado Livre confirmou, mas não alcança as sessões abertas, que ficam na memória do servidor | `sistema/contas/management/commands/apagar_conta.py:1` a `10` e `25` a `45`; `sistema/contas/acesso.py:108` a `125` |
| O histórico sai com a conta, pelo próprio banco, e um relatório que termina depois não traz a conta de volta | `sistema/relatorios/models.py:13` e `24`; `sistema/relatorios/historico.py:38` a `53` |
| "Apagar meu histórico" apaga só os relatórios | `sistema/relatorios/historico.py:80` a `83`; `sistema/relatorios/views.py:123` a `131` |
| "Sair" encerra só a sessão daquele navegador | `sistema/contas/views.py:45` a `48` |
| A página "Sua conta" | `sistema/contas/views.py:51` a `66`; `sistema/contas/templates/contas/conta.html` |

## Fontes

Consultadas em 15/10/2026.

- [Termos para desenvolvedores do Mercado Livre](https://developers.mercadolibre.com.ar/en_us/mercado-libre-developer-terms-and-conditions)
  (itens 2.2.4 e 14 relidos em 19/10/2026)
- [Formulário do aplicativo (Global Selling)](https://global-selling.mercadolibre.com/devsite/create-application)
  e [registro do aplicativo](https://developers.mercadolivre.com.br/en_us/register-your-application)
- [Programa de certificação (Developer Partner Program)](https://developers.mercadolibre.com.ar/en_us/developer-partner-program)
- [Autenticação: token de 6 horas, refresh token de uso único e de 6 meses, revogação](https://developers.mercadolivre.com.br/en_us/authentication-and-authorization)
- [Dados que vêm em `/users/me`](https://developers.mercadolibre.com.ar/devsite/manage-users-global-selling) e
  [nos pedidos](https://developers.mercadolivre.com.br/en_us/manage-sales)
- [Requisitos de segurança do Mercado Livre](https://developers.mercadolibre.com.ar/en_us/validations-and-security-requirements)
- [Resolução CD/ANPD nº 2/2022 (agentes de pequeno porte)](https://www.gov.br/palmares/pt-br/midias/arquivos-menu-acesso-a-informacao/legislacao/resolucao-cd-anpd-n2-2022.pdf)
- [Resolução CD/ANPD nº 15/2024 (incidentes)](https://www.legisweb.com.br/legislacao/?id=458235)
- [Prazo das cláusulas-padrão da Resolução CD/ANPD nº 19/2024](https://lefosse.com/noticias/alerta/transferencia-internacional-de-dados-prazo-para-adocao-das-clausulas-padrao-da-anpd-se-encerra-em-23-de-agosto/)
- [Resolução CD/ANPD nº 32/2026 (adequação da União Europeia)](https://www.trenchrossi.com/en/legal-alerts/brazil-and-the-european-union-mutually-recognize-adequacy-in-personal-data-protection-resolution-no-32-dated-january-26-2026/)
- [Regiões do Render](https://render.com/docs/regions) e [contrato de dados do Render](https://render.com/dpa)
- [Qual contrato vale para cada serviço do Firebase](https://firebase.google.com/terms/) e
  [Firebase Data Processing and Security Terms](https://firebase.google.com/terms/data-processing-terms)
- [Privacidade no Firebase: o Hosting guarda IPs "por alguns meses"](https://firebase.google.com/support/privacy)
- [Cloud Data Processing Addendum do Google Cloud](https://cloud.google.com/terms/data-processing-addendum) (lido pela
  thread de hospedagem)
- [Onde o Cloud Logging guarda os registros](https://docs.cloud.google.com/logging/docs/region-support)
- [Cobrança do Cloud Run: por pedido (padrão), a CPU só durante os pedidos](https://docs.cloud.google.com/run/docs/configuring/cpu-allocation)
  (lido em 16/10/2026)
- [Transparência nas transferências pela Resolução CD/ANPD nº 19/2024](https://www.mattosfilho.com.br/en/unico/regulates-international-data-transfers/)
- [Política de Privacidade do Google: "servidores em todo o mundo"](https://policies.google.com/privacy?hl=pt-BR)
  e [estruturas de transferência de dados](https://policies.google.com/privacy/frameworks?hl=pt-BR) (cláusulas da
  ANPD nos contratos de serviços comerciais, como o Google Workspace)
- [Campos dos registros de pedidos no Cloud Logging: `requestUrl` inclui a parte depois do `?`](https://docs.cloud.google.com/dotnet/docs/reference/Google.Cloud.Logging.Type/latest/Google.Cloud.Logging.Type.HttpRequest)
- [Declaração de Privacidade do Mercado Livre](https://www.mercadolivre.com.br/privacidade/declaracao-privacidade)
