# Privacidade e termos do Orzy

**Situação (15/10/2026):** rascunhos, escritos pelo Claude a partir do código. Nada está publicado.
Não é parecer jurídico: antes de abrir o site ao público, o ideal é um advogado revisar.

| Arquivo | O que é |
|---|---|
| [politica-de-privacidade.md](politica-de-privacidade.md) | Quais dados o site usa, para que, por quanto tempo e os direitos do vendedor (LGPD) |
| [termos-de-uso.md](termos-de-uso.md) | As regras de uso do site: o que ele faz, o que não faz, responsabilidades e foro |

Os textos descrevem o site como ele está no PR #5 (rascunho, commit `5cf1b8d`). Se o código mudar nos pontos da
tabela "De onde vem cada frase", os textos mudam junto.

Para achar o que falta, procure por `[PREENCHER` (só o Nicolas sabe) e `[CONFIRMAR` (depende de outra frente).

## O que só o Nicolas preenche

| Campo | Onde aparece | Observação |
|---|---|---|
| Nome completo do responsável, ou nome da empresa | Política (item 1) e Termos (início) | É quem responde pelos dados perante a lei. Precisa ser maior de 18 anos (ou emancipado), ou uma empresa. |
| CPF ou CNPJ | Política (item 1) e Termos (início) | Enquanto o Orzy for grátis, a LGPD pede a identificação do responsável; publicar o CPF não parece obrigatório (confirmar com advogado). Quando cobrar, o Decreto nº 7.962/2013 exige CPF ou CNPJ e endereço no site. |
| E-mail de contato | Política (itens 1 e 8) e Termos (item 14) | É o canal da LGPD. Alguém precisa ler: pedidos sobre dados têm resposta em até 15 dias. Pode ser um Gmail só do Orzy, de graça. |
| Cidade e estado | Termos (item 13) | Foro para quem não é consumidor. |
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
  Frankfurt e Singapura).

**Site: código e login:** os itens da seção seguinte.

**Página inicial:** link para a Política e os Termos no rodapé e a frase "Não somos o Mercado Livre". Sem o logotipo
do Mercado Livre (os termos deles só permitem as marcas conforme o manual de marcas do Mercado Livre) e sem ferramenta
de estatística (Google Analytics e parecidos) ou outros cookies. Se entrar alguma, a Política precisa mudar antes.

**Nicolas, na conta dele:** o caminho do menu do Mercado Livre onde o vendedor tira a permissão de um aplicativo
(Política, item 8). A documentação para desenvolvedores não diz.

## O que o site precisa ter para os textos valerem

1. Páginas `/privacidade` e `/termos` com os textos finais, no lugar do rascunho de `web/paginas.py`.
2. Junto ao botão **Conectar com Mercado Livre**: "Ao conectar, você aceita os Termos de Uso e confirma que leu a
   Política de Privacidade", com os dois links. Uma caixa de marcar é ainda melhor.
3. Links para os dois textos no rodapé de todas as páginas.
4. Data e hora em que cada relatório foi gerado, também na página do resultado (hoje ela só mostra o período). Os
   termos do Mercado Livre (5.3) pedem que o aplicativo diga com que frequência os dados são atualizados, e os Termos
   (item 6) prometem isso.
5. Apagar os relatórios com mais de 12 meses todo dia. Hoje isso só acontece quando o servidor liga
   (`web/servidor.py`), então um servidor ligado por muito tempo guardaria mais que os 12 meses prometidos.
6. Antes de guardar um dado novo, pedir e-mail, pôr cookies ou estatística, usar IA ou mudar a hospedagem de país,
   atualizar a Política.
7. Se o responsável virar empresa (CNPJ): guardar data, hora e IP de cada acesso por 6 meses, em sigilo (Marco Civil
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
| Transferência internacional com mecanismo válido (art. 33; Resoluções CD/ANPD nº 19/2024 e 32/2026) | Política item 5, conforme a hospedagem |
| Segurança e comunicação de incidentes (arts. 46 e 48; Resolução CD/ANPD nº 15/2024) | Política item 7 |
| Canal de comunicação no lugar do encarregado (Resolução CD/ANPD nº 2/2022, art. 11) | Política item 1 |

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
- Ler o e-mail de contato e responder pedidos em até 15 dias; apagar mensagens resolvidas há mais de 12 meses.
- Reler os termos do Mercado Livre e conferir se mudaram.

## De onde vem cada frase

Código do PR #5 (commit `5cf1b8d`, branch `claude/project-thread-y5cpt9`):

| O que os textos dizem | Onde está no código |
|---|---|
| O código de acesso fica só na memória do servidor | `web/sessoes.py:18` e `web/login.py` |
| O código de renovação é descartado | `web/login.py:52` |
| De `/users/me` ficam só o número e o apelido | `web/login.py:60` |
| O que o histórico guarda | `web/historico.py:15` a `30` |
| Histórico apagado com mais de 12 meses | `web/servidor.py:12` e `54` |
| Cookie `orzy_sessao`: HttpOnly, SameSite=Lax, Secure em HTTPS, dura 8 horas | `web/app.py:82` e `214` a `215`; `web/configuracao.py:66` |
| Até 300 anúncios por relatório | `web/configuracao.py:65` |
| Um relatório por vez por conta | `web/relatorios.py:73` |
| O registro do servidor anota só o caminho, sem o código do Mercado Livre | `web/servidor.py:40` a `42` |
| O que o relatório lê de cada anúncio | `painel-ml/meus_anuncios.py:28` |
| Dos pedidos, só o anúncio e a quantidade | `painel-ml/meus_anuncios.py:137` a `159` |
| "Não somos o Mercado Livre" no rodapé | `web/paginas.py:61` a `62` |

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
- [Declaração de Privacidade do Mercado Livre](https://www.mercadolivre.com.br/privacidade/declaracao-privacidade)
