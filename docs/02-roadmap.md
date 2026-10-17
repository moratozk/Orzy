# 02 · Roadmap

O objetivo do Orzy é ser um ERP completo para quem vende no Mercado Livre (e depois na Shopee), com a Orzy
Intelligence analisando os dados. Hoje ele é um painel que mostra quais anúncios vendem e o que mudar em cada um; o
ERP entra módulo por módulo a partir da fase 4.
O Nicolas desenvolve e testa com a conta conectada no PC dele e, para ter mais números,
com vendedores que autorizem o app.

Cada fase só começa quando a anterior estiver funcionando com dados reais.
Antes de escrever código grande numa fase, o plano dela (3 a 6 passos) é mostrado e espera o ok do Nicolas.

Rumo, do Plano de Desenvolvimento do Nicolas (15/10/2026), usado como referência e não como regra ("é só um plano
inicial"): primeiro o Orzy observa, depois entende e recomenda, e só com autorização do vendedor executa. A ordem das
fases 4 a 7 saiu desse plano e foi aprovada por ele em 15/10/2026. Em 16/10/2026 ele definiu o objetivo: "um sistema
erp COMPLETO junto com a integração de uma ia que faz a análise dos dados", e que, ao criar a conta, um botão leve ao
Mercado Livre e o Orzy puxe tudo para o sistema. As fases 4 a 10 abaixo saíram desse pedido e foram aprovadas por ele
em 17/10/2026. Planos, comparação e proposta em `/mnt/project-files/orzy/plano/`.

## Fase 1 · Painel do Mercado Livre funcionando (concluída em 14/10/2026)

Conectar na conta e gerar o relatório de anúncios ativos com visitas, vendas e conversão,
separando os anúncios em 5 situações (visita sem venda, converte pouco, pouca visita,
vende mas pouco visto, vendendo bem).

- [x] Código do painel no repositório (`painel-ml/`)
- [x] Testes com Mercado Livre simulado (`testes/`)
- [x] Criar o app "OrzyApp" no Mercado Livre, na conta do Nicolas, e conectar (14/10/2026)
- [x] Rodar o relatório numa conta real (1 anúncio ativo, 14/10/2026)
- [ ] Conferir visitas e vendas numa conta com mais anúncios e vendas, de um vendedor que autorize o app
  (fica para quando aparecer; não segura a fase 2)

## Fase 2 · Sugestões de verdade para cada anúncio (concluída em 15/10/2026)

Plano aprovado pelo Nicolas em 14/10/2026. Antes, o texto de "o que olhar" era igual para todos os anúncios
da mesma situação. Agora o programa lê o próprio anúncio e diz o que mudar nele, usando só regras (custo zero).

- [x] Ler título, fotos, ficha técnica, frete grátis e tipo (Grátis, Clássico ou Premium) de cada anúncio,
  e os campos da ficha técnica de cada categoria
- [x] Ler a nota de qualidade que o próprio Mercado Livre dá ao anúncio e o que ele pede para melhorar
- [x] Regras num arquivo separado (`painel-ml/analise.py`), para o site da fase 3 usar as mesmas
- [x] Colunas `o_que_mudar` e `qualidade_ml` no CSV, com os anúncios que mais precisam de mudança primeiro
- [x] Testes com o Mercado Livre simulado
- [x] Rodar no anúncio real do Nicolas, o microfone de lapela (15/10/2026: a nota do Mercado Livre veio; a sugestão
  de fotos repetida foi corrigida)
- [x] Conferir as sugestões com o anúncio aberto no site (15/10/2026: 1 foto, título curto e frete grátis batem)
- [ ] Ver a contagem da ficha técnica na tela ("Ficha técnica: X de Y campos") na próxima rodada. Não segura a fase.

## Fase 3 · Site no orzy.com.br (em construção, sem publicar)

Decidido pelo Nicolas em 14/10/2026: é aqui que o Orzy vira site, para outros vendedores usarem sem instalar nada.
Plano em 5 passos, custos, LGPD e decisões em [07-fase-3-plano.md](07-fase-3-plano.md). O código está num PR de
rascunho: não entra no main nem vai para o ar antes do ok do Nicolas. Decidido por ele em 15/10/2026: o site só vai
ao ar quando estiver quase pronto (95%), sem endereço temporário.

Ordem decidida pelo Nicolas em 15/10/2026: primeiro o **site base**, funcionando; depois aprimorar até um site
realmente bonito, com a identidade visual (logo, cores e letras) da thread "Identidade visual e logo". O visual
de agora, inclusive o da página inicial, é só uma base, nada perto do modelo final: não vale gastar tempo polindo.

- [x] Código do site em rascunho (`web/`): login, relatório, histórico e testes com o Mercado Livre simulado
- [x] Página inicial base (primeiro protótipo, aprovado em 15/10/2026; não é o visual final)
- [x] Política de Privacidade e Termos de Uso em rascunho (`docs/legal/`), já mostrados no site
- [x] Recomendação de hospedagem com custos em reais
- [x] Terminar o site base (aprovado em 15/10/2026):
  - [x] segurança das sessões
  - [x] páginas internas funcionando no celular
  - [x] comparação de relatórios no histórico (o que mudou em cada anúncio desde o relatório anterior)
  - [x] histórico no Firestore (testado com um Firestore simulado; o de verdade, só na hora de publicar)
- [x] Busca pelo título e filtro por situação na tabela "Todos os anúncios" (do plano de 15/10/2026)
- [x] Identidade visual: o Nicolas escolheu a Anel em 15/10/2026 (thread "Identidade visual e logo"). No site base
  entraram só a logo, as cores, os ícones e a fonte Geist
- [x] Contagens do beta no site: a página `/contagens`, só para a conta do Nicolas, mostra contas com relatório
  guardado, anúncios por conta, logins e relatórios sem erro e com erro (só contagens, sem guardar dado novo do
  vendedor). Com isso, o site base está pronto
- [x] Ajustes pedidos pela revisão da Política de Privacidade (16/10/2026): a sessão com login acaba 8 horas depois
  do login, mesmo em uso, e as contagens do beta são apagadas depois de 12 meses
- [ ] Visual final: refazer as páginas com a identidade escolhida, até um site realmente bonito
- [ ] Escolher a hospedagem e adaptar o código a ela
- [ ] Antes de abrir ao público: monitoramento do servidor, cópia de segurança do histórico e aviso de falha
- [ ] Preencher os textos legais (nome e CPF ou CNPJ do responsável e a hospedagem; o e-mail de contato já está) e,
  se o Nicolas quiser, revisão de advogado
- [ ] Cadastrar a Redirect URI do site no OrzyApp e lançar, testando primeiro com a conta do Nicolas
- [ ] Beta fechado com 3 a 5 vendedores pequenos (dezenas ou centenas de anúncios), contando contas conectadas,
  relatórios concluídos sem erro e anúncios por conta (só contagens, sem guardar dado novo do vendedor)

- O vendedor entra no orzy.com.br e clica em **Conectar com Mercado Livre**. Ninguém precisa criar app.
- Um servidor pequeno guarda o Client Secret do app do Orzy. O Secret nunca vai dentro de um programa distribuído.
- O app "OrzyApp" do teste é o mesmo: ganha o Redirect URI do site e um Client Secret novo, que só o servidor conhece.
- O relatório e as sugestões aparecem no navegador, no lugar do CSV.
- Cada relatório fica guardado, para ver se um anúncio melhorou depois de uma mudança. Esse histórico é a base dos
  alertas da fase 4 e do ERP da fase 5.

Antes de começar, o plano da fase mostra:

- onde hospedar o site e o servidor, com o custo em reais por mês (existem opções grátis, com limites);
- como cuidar dos dados dos vendedores (LGPD e política de privacidade);
- se o app "OrzyApp" continua na conta do Nicolas ou passa para uma conta de empresa: o Mercado Livre recomenda
  criar o app na conta dona da solução, de preferência de empresa, para evitar problema de transferência depois.

## Fase 4 · Conta, importação completa e Orzy Intelligence

Pedido do Nicolas em 16/10/2026: ao criar a conta, um botão leva ao Mercado Livre, o vendedor autoriza e o Orzy puxa
tudo para o sistema. É também a primeira versão útil do plano dele: conexão, histórico e alertas.

- Antes de tudo: trocar o site para Django com PostgreSQL (Cloud SQL em São Paulo), levando o login, os relatórios,
  as regras e o histórico do beta. É quando o Orzy passa a guardar os dados das contas. Custo em reais aprovado antes.
- Conta criada no clique em "Conectar com Mercado Livre", sem senha. O refresh token fica guardado com criptografia
  e a chave fora do banco. Ele é de uso único: só um processo por vendedor renova de cada vez, e o novo é salvo antes
  de qualquer outra coisa.
- Primeira carga em segundo plano, com progresso: anúncios de todos os status, variações, descrição, ficha técnica,
  fotos (só os links do Mercado Livre), estoque, preço, frete, vendas dos últimos 12 meses (sem dados pessoais do
  comprador), visitas dos últimos 150 dias, nota de qualidade e reputação
- Sincronia todo dia (os termos do Mercado Livre pedem dados atualizados a cada 24 horas) e pelas notificações do
  Mercado Livre; registro das falhas
- Desconectar e apagar tudo, também quando o vendedor tira a permissão no Mercado Livre
- Alertas de queda e de oportunidade, comparando períodos equivalentes, sem afirmar a causa, por ordem de impacto e
  urgência, numa central de alertas (aviso por e-mail ou WhatsApp a decidir, com custo)
- Guardar cada recomendação e o que aconteceu depois; o vendedor marca se ajudou ou não
- **Orzy Intelligence (o módulo de IA, pago por uso):** só onde regra não resolve: explicar os achados e sugerir
  título e descrição. Pedido do Nicolas (15/10/2026): tem de ser muito eficiente e o mais otimizada possível. Regras
  de custo e de otimização em [05-custos.md](05-custos.md). Nunca recebe dados de compradores. Até ela existir, as
  sugestões do relatório são regras fixas e o site não as chama de IA. Antes de ligar, a Política de Privacidade
  precisa dizer qual empresa faz a IA, em que país e com quais cláusulas da ANPD.

Antes de começar: Política de Privacidade e Termos atualizados (conta guardada, dados importados, IA) e o custo em
reais por mês (banco, agendador, IA e aviso).

## Fase 5 · Base do ERP: empresa, produtos, custos e margem

- Login com e-mail e senha, outros usuários com papéis (dono, operador) e mais de uma conta do Mercado Livre na mesma
  empresa
- Produtos (SKU, variações, kits, código de barras, peso e medidas) ligados aos anúncios: um produto em vários anúncios
- Custos: produto, tarifa de venda, frete, imposto estimado e despesas
- Margem por venda, anúncio e produto, num painel com menu lateral
- Orzy Intelligence: margem baixa, promoção ou frete grátis que come o lucro, preço sugerido (só sugestão)

Antes de começar: decidir como cobrar dos vendedores (o Orzy tem custo fixo desde a fase 4).

## Fase 6 · Pedidos, estoque e compras

- Pedidos com o tipo de envio (Full, Flex, coleta), cancelamentos e devoluções
- Estoque por produto e depósito, com entradas, saídas, ajustes, inventário e estoque mínimo; o do Full separado
- Compras e fornecedores: pedido de compra, entrada de mercadoria e custo médio
- Orzy Intelligence: previsão de ruptura, sugestão de compra e produto parado

## Fase 7 · Financeiro

- Contas a pagar e a receber, categorias e fluxo de caixa
- Repasses do Mercado Pago por venda, com tarifas, frete e retenções (a validar: acesso pela API do Mercado Pago)
- Resultado do mês e exportação para o contador
- Orzy Intelligence: tarifa fora do normal e previsão de caixa

## Fase 8 · Mudanças no Mercado Livre com aprovação

Era a fase 6 até 17/10/2026.

- O vendedor revisa e aprova cada mudança; nada muda sozinho
- Preço, estoque, título, descrição e outros campos que a API deixa, conferindo margem (fase 5) e estoque (fase 6)
- Registro de quem aprovou, quando, o valor antigo e o novo; desfazer quando a API deixar
- Permissão de escrita no app (os vendedores autorizam de novo) e mudança nos Termos e na Política, que hoje dizem
  que o Orzy só lê a conta

## Fase 9 · Shopee e multicanal

Era a fase 7 até 17/10/2026 (e a fase 4 até 15/10/2026).

- Shopee em todos os módulos: anúncios, pedidos, estoque e financeiro
- Estoque único entre os canais, usando a escrita da fase 8

## Fase 10 · Nota fiscal

- Emitir a NF-e das vendas por um emissor que já existe (o faturador do próprio Mercado Livre ou uma API de nota
  fiscal paga por nota). O Orzy não constrói emissor próprio: a nota muda com a reforma tributária até 2033
- Entrada das compras pelo XML da nota do fornecedor
- Aqui o Orzy passa a tratar dados dos compradores (nome, CPF e endereço): Política e Termos mudam e o advogado revisa
  antes. Cada vendedor precisa do próprio certificado digital A1
- Se os vendedores do beta pedirem nota fiscal antes, ela pode subir para logo depois do financeiro

## Depois (sem ordem definida ainda)

- Atendimento: perguntas e mensagens, com sugestão de resposta da Orzy Intelligence
- Aplicativo de celular e outros canais (Amazon, Magalu, loja própria)
- Planos pagos por volume de anúncios, contas conectadas e recursos de IA
