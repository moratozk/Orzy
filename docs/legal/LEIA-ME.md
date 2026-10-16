# Privacidade e termos do Orzy

**Situação (16/10/2026):** rascunhos, escritos pelo Claude a partir do código. Nada está publicado.
Não é parecer jurídico: antes de abrir o site ao público, o ideal é um advogado revisar.

| Arquivo | O que é |
|---|---|
| [politica-de-privacidade.md](politica-de-privacidade.md) | Quais dados o site usa, para que, por quanto tempo e os direitos do vendedor (LGPD) |
| [termos-de-uso.md](termos-de-uso.md) | As regras de uso do site: o que ele faz, o que não faz, responsabilidades e lei aplicável |

Os textos descrevem o site como ele está no PR #5 (rascunho, commit `9c3bfdc`, conferido em 16/10/2026). Se o código
mudar nos pontos da tabela "De onde vem cada frase", os textos mudam junto.

Para achar o que falta, procure por `[PREENCHER` (só o Nicolas sabe) e `[CONFIRMAR` (depende de outra frente).

**Como o site mostra os textos:** as páginas `/privacidade` e `/termos` leem os dois arquivos desta pasta a cada
visita (`web/legal.py`). O site entende só parte do Markdown: títulos, parágrafos, listas de um nível (a continuação
de um item vai recuada), citações (`>`), tabelas, negrito, código e links. Não use itálico, lista dentro de lista,
linha horizontal nem imagem. Os links para `politica-de-privacidade.md` e `termos-de-uso.md` viram `/privacidade` e
`/termos`; outros links relativos, como o deste LEIA-ME, aparecem como texto.

## O que só o Nicolas preenche

| Campo | Onde aparece | Observação |
|---|---|---|
| Nome completo do responsável, ou nome da empresa | Política (item 1) e Termos (início) | É quem responde pelos dados perante a lei. Precisa ser maior de 18 anos (ou emancipado), ou uma empresa. |
| CPF ou CNPJ | Política (item 1) e Termos (início) | Enquanto o Orzy for grátis, a LGPD pede a identificação do responsável; publicar o CPF não parece obrigatório (confirmar com advogado). Quando cobrar, o Decreto nº 7.962/2013 exige CPF ou CNPJ e endereço no site. |
| Data de publicação | Os dois | Muda a cada versão. |

Já perguntado no thread "Site: código e login": se haverá revisão de advogado antes do público.

## O que depende das outras frentes

**Hospedagem e domínio:** o nome da empresa de hospedagem (Política, item 4), o país dos servidores (item 5) e por
quanto tempo ela guarda registros de acesso e cópias de segurança (itens 2.4 e 6). Texto do item 5 para cada caso:

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
- **Google (recomendação da thread de hospedagem, 15/10/2026, ainda não decidida):** servidor no Cloud Run e histórico
  no Firestore, os dois em São Paulo, contratados com a Google Cloud Brasil Computação e Serviços de Dados Ltda.
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
  guardada 7 dias em São Paulo: um dado apagado pode ficar até 7 dias nas cópias, e depois o Google conclui a exclusão
  em até 180 dias. Um robô abre `/saude` a cada 5 minutos, então o servidor não desliga quando ninguém usa o site, e a
  sessão dura até **Sair** ou 8 horas depois do login, como a Política já diz (ela ainda acaba se o servidor reiniciar).
  Na cobrança por pedido, o padrão do Cloud Run, a CPU só funciona durante algum pedido, e a limpeza das sessões anda
  com os pedidos do robô; para as 8 horas valerem, a thread do código faz a limpeza na nuvem apagar as sessões 6 minutos
  antes do prazo, no lançamento. Os avisos de erro por e-mail ao responsável não trazem dado de vendedor; se um dia
  trouxerem, a Política precisa contar. Só com o Firebase Hosting, o cookie passa a se chamar `__session`.
- **Registro de quem apagou o histórico** (proposta da thread de hospedagem, aceita por esta thread em 16/10/2026):
  quando alguém apaga o histórico, o número da conta e a hora ficam 8 dias num registro à parte, em São Paulo, só para
  apagar de novo os relatórios dessa conta se for preciso voltar uma cópia de segurança. Sem ele, voltar uma cópia
  traria de volta relatórios que a pessoa apagou. Quando o código fizer isso, entram na Política uma frase no item 2.4,
  uma linha no item 3 (cumprimento de obrigação legal: garantir a eliminação pedida, arts. 7º, II, e 18, VI) e uma linha
  no item 6 (8 dias).

**Site: código e login:** os itens da seção seguinte.

**Página inicial:** link para a Política e os Termos no rodapé e a frase "Não somos o Mercado Livre". Sem o logotipo
do Mercado Livre (os termos deles só permitem as marcas conforme o manual de marcas do Mercado Livre) e sem ferramenta
de estatística (Google Analytics e parecidos) ou outros cookies. Se entrar alguma, a Política precisa mudar antes.

**Nicolas, na conta dele:** o caminho do menu do Mercado Livre onde o vendedor tira a permissão de um aplicativo
(Política, item 8). A documentação para desenvolvedores não diz.

## O que o site precisa ter para os textos valerem

Já feito no PR #5 (commit `9c3bfdc`, ainda em rascunho):

1. Páginas `/privacidade` e `/termos`, que mostram os arquivos desta pasta.
2. Junto de cada botão **Conectar com Mercado Livre**: "Ao conectar, você aceita os Termos de Uso e confirma que leu a
   Política de Privacidade", com os dois links. Não há caixa de marcar: o Nicolas aprovou a página inicial assim, e dá
   para pôr uma depois, se um advogado preferir.
3. Links para os dois textos no rodapé de todas as páginas.
4. Na página do resultado, a data e a hora em que os dados foram buscados; no histórico, o aviso de que cada relatório
   mostra os anúncios como estavam naquele dia. Os termos do Mercado Livre (5.3) pedem que o aplicativo diga com que
   frequência os dados são atualizados, e os Termos (item 6) prometem isso.
5. Relatórios e contagens do beta com mais de 12 meses apagados ao ligar o servidor e depois a cada 24 horas.
6. O e-mail de contato no rodapé de todas as páginas.
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

Regras que continuam valendo:

- Antes de guardar um dado novo, pedir e-mail, pôr cookies ou estatística, usar IA ou mudar a hospedagem de país,
  atualizar a Política.
- `ORZY_HORAS_SESSAO` muda o prazo da sessão e do cookie (padrão: 8 horas). Mais de 8 só depois de mudar a Política
  (itens 2.4 e 6), que promete 8.
- Se o responsável virar empresa (CNPJ): guardar data, hora e IP de cada acesso por 6 meses, em sigilo (Marco Civil
  da Internet, art. 15). Hoje o site não guarda IP.

## O que o Mercado Livre exige

Lido em 15/10/2026 nos [termos para desenvolvedores](https://developers.mercadolibre.com.ar/en_us/mercado-libre-developer-terms-and-conditions)
(a página em inglês; não tem data de versão):

| Item dos termos | O que pede | Como o Orzy cumpre |
|---|---|---|
| 6 | Cumprir a LGPD; usar os dados só para a finalidade; o usuário do Mercado Livre que autoriza é o controlador e o desenvolvedor segue as instruções dele; subcontratados com a mesma segurança; avisar o Mercado Livre se uma autoridade pedir dados | Política itens 2.3, 3 e 4. Avisar o Mercado Livre fica com o responsável, se acontecer |
| 10 | Medidas de segurança para dados pessoais (nomes, e-mails), credenciais e apelidos | Política item 7 |
| 2.2.1.3 | Cópias intermediárias só as necessárias, apagadas de vez quando não servem mais | Token só na memória; cadastro e compradores descartados na hora |
| 2.2.4 | Revogar o acesso aos dados de quem sair; não usar "mercado", "libre", "livre", "payment", "shipments" nem "credit" no nome ou no visual do aplicativo | "Sair" e "Apagar meu histórico"; o nome Orzy está fora da lista |
| 4.1 | Deixar sempre claro que o aplicativo não pertence ao Mercado Livre; marcas do Mercado Livre só conforme o manual de marcas deles | Termos item 2 e rodapé do site |
| 5.2 e 5.3 | Informação não pública do usuário só com autorização dele; conteúdo atualizado pelo menos a cada 24 horas; o aplicativo informa a frequência de atualização | Termos item 6 e site item 4 acima |
| 2.2.2 | Client Secret em sigilo; avisar o Mercado Livre se houver uso indevido | Secret só no ambiente do servidor |
| 7.9 | Não guardar dados de cartão nem números de documento sem autorização | O Orzy não guarda |
| 9 | O Mercado Livre pode auditar e suspender o acesso por suspeita de falha de segurança | Termos item 2 |
| 14 | Se o Mercado Livre cortar o acesso: parar de usar a API e destruir as cópias e os dados pessoais obtidos | Apagar o histórico nesse caso |
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
- **E-mail de contato:** orzy.suporte@gmail.com, criado pelo Nicolas em 15/10/2026. É um Gmail comum: segue os termos de
  consumidor do Google, sem contrato de tratamento de dados nem as cláusulas-padrão da ANPD, e as mensagens podem ficar
  em servidores fora do Brasil (a Política diz isso nos itens 4 e 5). O Google diz que pode pôr essas cláusulas nos
  contratos de serviços comerciais, como o Google Workspace, que é pago. Antes de abrir ao público, confirmar com o
  advogado se a transferência das mensagens se apoia no art. 33, IX, da LGPD (necessária para responder a quem
  escreveu); se não, trocar por um e-mail com contrato de dados e ajustar os itens 4 e 5 da Política.
- Ler o e-mail de contato e responder pedidos em até 15 dias; apagar mensagens resolvidas há mais de 12 meses.
- Reler os termos do Mercado Livre e conferir se mudaram.

## De onde vem cada frase

Código do PR #5 (commit `9c3bfdc`, branch `claude/project-thread-y5cpt9`):

| O que os textos dizem | Onde está no código |
|---|---|
| O código de acesso fica só na memória do servidor | `web/sessoes.py:24` e `web/login.py` |
| O código de renovação é descartado | `web/login.py:52` |
| De `/users/me` ficam só o número e o apelido | `web/login.py:60` |
| O que o histórico guarda (SQLite no PC e no Render; Firestore no Cloud Run, com os mesmos campos) | `web/historico.py:19` a `36`; `web/historico_firestore.py:189` a `200` |
| Histórico e contagens do beta apagados com mais de 12 meses, ao ligar e depois a cada 24 horas | `web/historico.py:17` e `127` a `137`; `web/historico_firestore.py:246` a `255`; `web/servidor.py:56` a `70`, `88` a `92` e `104`; no Firestore, os relatórios também têm o campo `expira_em` (`web/historico_firestore.py:194`) |
| O que mudou desde o relatório anterior do mesmo período, sem dizer por quê | `web/comparacao.py`; `web/historico.py:107` a `118`; `web/paginas.py:593` a `594` |
| Cookie `orzy_sessao`: HttpOnly, SameSite=Lax, Secure em HTTPS, dura 8 horas | `web/app.py:115`, `131` e `283` a `287`; `web/configuracao.py:81` |
| Sessão sem login apagada depois de 15 minutos; código novo depois do login | `web/sessoes.py:15` a `16`, `51` a `60` e `80` a `93`; `web/app.py:128` |
| Sessão com login apagada do servidor no máximo 8 horas depois do login, mesmo em uso, conferida a cada minuto | `web/sessoes.py:27`, `58` e `74` a `93`; `web/servidor.py:73` a `92` e `104`; `web/app.py:123` a `131` |
| Até 300 anúncios por relatório | `web/configuracao.py:80` |
| Um relatório por vez em cada conexão | `web/relatorios.py:79` a `80` |
| O registro do servidor anota só o caminho, sem o código do Mercado Livre nem a busca | `web/servidor.py:49` a `53`; `web/app.py:66` |
| Contagens do beta: só números por dia, sem conta, apelido nem anúncio | `web/contagens.py:14` a `20`; `web/relatorios.py:91` a `119`; `web/app.py:126`; `web/historico.py:38` a `43` e `141` a `147` |
| Página `/contagens` só para as contas de `ORZY_CONTAS_ADMIN`, sem mostrar de quem são os números | `web/app.py:237` a `242`; `web/configuracao.py:68` a `72`; `web/historico.py:157` a `162` |
| O que o relatório lê de cada anúncio | `painel-ml/meus_anuncios.py:28` |
| Dos pedidos, só o anúncio e a quantidade | `painel-ml/meus_anuncios.py:137` a `159` |
| "Não somos o Mercado Livre", os links para os dois textos e o e-mail de contato no rodapé | `web/paginas.py:14` e `85` a `86` |
| Aviso de aceite junto de cada botão Conectar | `web/paginas.py:104` a `105` |
| Data e hora em que os dados foram buscados | `web/relatorios.py:56` e `web/paginas.py:471` a `475` |
| O histórico mostra como os anúncios estavam no dia | `web/paginas.py:517` e `615` |
| Fonte, ícones e imagens saem do próprio site, sem serviço de fora na página | `web/app.py:19` a `27` e `37` a `38` |
| O site mostra os textos desta pasta | `web/legal.py:12` a `13` e `web/app.py:83` a `84` |

## Fontes

Consultadas em 15/10/2026.

- [Termos para desenvolvedores do Mercado Livre](https://developers.mercadolibre.com.ar/en_us/mercado-libre-developer-terms-and-conditions)
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
