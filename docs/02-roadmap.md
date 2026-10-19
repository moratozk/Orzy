# 02 · Roadmap

O objetivo do Orzy é ser um ERP completo para quem vende no Mercado Livre (e depois na Shopee), com a Orzy
Intelligence analisando os dados. Hoje ele é um painel que mostra quais anúncios vendem e o que mudar em cada um; o
ERP entra módulo por módulo a partir da fase 4.
Decisão do Nicolas (17/10/2026): o site só vai ao ar quando o sistema inteiro estiver funcionando, com o painel, a
integração com o Mercado Livre, o pagamento, a assinatura e a IA. Antes, ele testa e dá uma conta demo para o
professor dele. Ele desenvolve e testa com a conta conectada no PC dele e, do fim da fase 4 em diante, num endereço
de teste fechado.

Cada fase só começa quando a anterior estiver funcionando com dados reais.
Antes de escrever código grande numa fase, o plano dela (3 a 6 passos) é mostrado e espera o ok do Nicolas.

Rumo, do Plano de Desenvolvimento do Nicolas (15/10/2026), usado como referência e não como regra ("é só um plano
inicial"): primeiro o Orzy observa, depois entende e recomenda, e só com autorização do vendedor executa. Em 16/10/2026
ele definiu o objetivo: "um sistema erp COMPLETO junto com a integração de uma ia que faz a análise dos dados", e que,
ao criar a conta, um botão leve ao Mercado Livre e o Orzy puxe tudo para o sistema. Os módulos do ERP saíram desse
pedido e foram aprovados por ele em 17/10/2026. Em 18/10/2026 ele aprovou a ordem abaixo, com tudo pronto antes de
lançar e sem beta com vendedores convidados: as fases 4 a 7 como antes, depois planos e pagamento (8), testes
completos (9) e o lançamento (10). Mudanças no Mercado Livre, Shopee e nota fiscal ficam para depois do lançamento.
Planos, comparação e propostas em `/mnt/project-files/orzy/plano/`.

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

## Fase 3 · Site base (pronto no PR #5; o lançamento foi para a fase 10)

Decidido pelo Nicolas em 14/10/2026: é aqui que o Orzy vira site, para outros vendedores usarem sem instalar nada.
Plano em 5 passos, custos, LGPD e decisões em [07-fase-3-plano.md](07-fase-3-plano.md). O código está no PR #5, que
entra no main como base da fase 4 (ok do Nicolas em 18/10/2026). Entrar no main não põe nada no ar: o repositório não
publica sozinho.

Ordem decidida pelo Nicolas em 15/10/2026: primeiro o **site base**, funcionando; depois aprimorar até um site
realmente bonito, com a identidade visual (logo, cores e letras) da thread "Identidade visual e logo". O visual
de agora, inclusive o da página inicial, é só uma base, nada perto do modelo final: não vale gastar tempo polindo.

- [x] Código do site em rascunho (`web/`): login, relatório, histórico e testes com o Mercado Livre simulado. Em
  19/10/2026 ele passou para Django em `sistema/` (fase 4, passo 1) e o `web/` saiu do repositório
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

O que faltava para abrir (o visual final, a hospedagem, o monitoramento, os textos legais preenchidos, a Redirect URI
do site e o lançamento) foi para as fases 4 e 10 em 18/10/2026, e o beta fechado com 3 a 5 vendedores saiu (escolha
do Nicolas: "Sem convidados").

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
tudo para o sistema. Plano em 5 passos aprovado por ele em 18/10/2026
(`/mnt/project-files/orzy/plano/nova-ordem-sistema-completo.md`, seção 2).

1. **Base nova (pronta em 19/10/2026, PR #12):** o PR #5 entrou no main e o site passou para Django com PostgreSQL
   (num plano grátis até o lançamento) em `sistema/`, levando o login, os relatórios, as regras e o histórico, já
   com o visual novo da thread "Identidade visual e logo" (`/mnt/project-files/orzy/marca/visual-final/`). Os
   testes passaram para o sistema novo, e o site antigo (`web/`) saiu. O banco guarda o mesmo que o site base
   guardava (o histórico e as contagens): os dados das contas começam a ser guardados no passo 2. O que falta para
   o endereço de teste está em `sistema/LEIA-ME.md` ("Antes de publicar").
2. **Conta e acesso guardado (pronto em 19/10/2026):** a conta é criada no clique em "Conectar com Mercado Livre",
   sem senha. O refresh token fica no banco cifrado (AES-256-GCM), com a chave fora do banco, numa variável de
   ambiente (`ORZY_CHAVE_ACESSO`); o token de acesso continua só na memória. Ele é de uso único: a linha da conta
   fica travada no banco durante a renovação, e o novo é salvo antes de o token de acesso ser usado. O Orzy renova
   cada conta uma vez por dia, para o refresh token não vencer e para perceber quem tirou a permissão. A página "Sua
   conta" (o círculo com as iniciais, no topo) mostra o que fica guardado e tem o "Desconectar e apagar tudo": apaga
   a conta, o acesso e o histórico, encerra as sessões em todos os navegadores e tira a permissão do Orzy no Mercado
   Livre. Quando o Mercado Livre recusa o acesso guardado (permissão tirada e senha trocada dão o mesmo erro), o
   Orzy apaga o acesso na hora e encerra as sessões; a conta e o histórico saem 30 dias depois, se a pessoa não
   conectar de novo. A Política de Privacidade ainda não fala disso: as mudanças vão para a thread "Privacidade e
   termos", prontas antes de outra pessoa usar.
3. **Importação completa:** primeira carga em segundo plano, com progresso: anúncios de todos os status, variações,
   descrição, ficha técnica, fotos (só os links do Mercado Livre), estoque, preço, frete, vendas dos últimos 12 meses
   (sem dados pessoais do comprador), visitas dos últimos 150 dias, nota de qualidade e reputação. Conferida na conta
   do Nicolas com um programa de conferência no PC, que mostra só contagens e não pede nada novo para instalar.
4. **Sincronia e alertas:** atualização todo dia (os termos do Mercado Livre pedem dados atualizados a cada 24 horas)
   e pelas notificações do Mercado Livre, com registro das falhas. Alertas de queda e de oportunidade, comparando
   períodos equivalentes, sem afirmar a causa, por ordem de impacto e urgência, numa central de alertas (aviso por
   e-mail ou WhatsApp a decidir, com custo). Cada recomendação fica guardada com o que aconteceu depois, e o vendedor
   marca se ajudou ou não.
5. **Orzy Intelligence e endereço de teste:** a IA (o módulo pago por uso) entra só onde regra não resolve: explicar
   os achados e sugerir título e descrição. Pedido do Nicolas (15/10/2026): tem de ser muito eficiente e o mais
   otimizada possível; regras de custo em [05-custos.md](05-custos.md). Nunca recebe dados de compradores. No fim da
   fase, com o ok do Nicolas e o custo em reais, o sistema vai para um endereço de teste fechado, só para a conta dele
   (o orzy.com.br não muda).

No começo da fase, as mudanças da Política de Privacidade e dos Termos (conta guardada, dados importados, IA) vão para
a thread "Privacidade e termos", prontas antes de outra pessoa usar. Antes de a IA ligar, a Política diz qual empresa
faz a IA, em que país e com quais cláusulas da ANPD. Até a IA existir, as sugestões do relatório são regras fixas e o
site não as chama de IA.

## Fase 5 · Base do ERP: empresa, produtos, custos e margem

- Login com e-mail e senha, outros usuários com papéis (dono, operador) e mais de uma conta do Mercado Livre na mesma
  empresa
- Produtos (SKU, variações, kits, código de barras, peso e medidas) ligados aos anúncios: um produto em vários anúncios
- Custos: produto, tarifa de venda, frete, imposto estimado e despesas
- Margem por venda, anúncio e produto, num painel com menu lateral
- Orzy Intelligence: margem baixa, promoção ou frete grátis que come o lucro, preço sugerido (só sugestão)

Como cobrar dos vendedores fica para a fase 8.

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

## Fase 8 · Planos, assinatura e pagamento

Nova em 18/10/2026: o lançamento já sai com a assinatura funcionando.

- Rever os preços e o que cada plano inclui: os de 17/10/2026 (Grátis até 10 anúncios, Essencial R$ 29,90 até 50,
  Profissional R$ 59,90 até 300) eram para um lançamento só com o relatório. O plano Grátis com limite continua.
  Ideias em `/mnt/project-files/orzy/plano/precos-e-planos.md`
- A página "Escolha seu plano" como primeiro passo de "Criar conta"
- Assinatura mensal (e anual, se o Nicolas quiser) pelo Mercado Pago: cobrança automática, aviso de pagamento
  recusado, troca de plano, cancelamento a um clique e os limites de cada plano no sistema
- Testada no modo de teste do Mercado Pago, com usuários e cartões de teste: ninguém paga de verdade
- Termos com preço, renovação, cancelamento, reembolso e o direito de arrependimento de 7 dias do Código de Defesa do
  Consumidor

## Fase 9 · Testes completos

Nova em 18/10/2026. Sem beta com vendedores convidados (escolha do Nicolas): o site abre logo depois destes testes.

- Revisão de segurança do sistema inteiro antes de qualquer outra pessoa entrar
- Testes de ponta a ponta do Nicolas com a conta dele: criar conta, importar, alertas, ERP, assinar um plano com
  cartão de teste, cancelar e apagar tudo
- Uma loja de teste do Mercado Livre (usuários de teste) para simular vendas, devoluções e estoque sem mexer na conta
  dele
- Conta demo para o professor do Nicolas, com uma loja de exemplo de dados inventados. Se ele quiser conectar a conta
  dele do Mercado Livre, a Política e os Termos já estão publicados
- O Nicolas ajusta aos poucos com o que o professor disser, e cada ajuste é testado de novo

## Fase 10 · Lançamento no orzy.com.br

- Política e Termos revisados pelo advogado, com o nome e o CPF ou CNPJ do responsável
- Banco pago, porta de entrada do orzy.com.br, DNS, OrzyApp (Redirect URI do site e logo nova), monitoramento, cópia
  de segurança e Mercado Pago de verdade (conta verificada, CNPJ e contador para cobrar). Cada passo com o ok do
  Nicolas e o custo em reais antes
- Como o ERP e a IA já existem, o site anuncia os dois desde o primeiro dia

## Depois do lançamento

Na ordem já aprovada, ajustada pelo que os primeiros clientes pedirem. Cada uma ganha um número de fase quando
começar.

### Mudanças no Mercado Livre com aprovação

Era a fase 8 até 18/10/2026 (e a fase 6 até 17/10/2026).

- O vendedor revisa e aprova cada mudança; nada muda sozinho
- Preço, estoque, título, descrição e outros campos que a API deixa, conferindo margem (fase 5) e estoque (fase 6)
- Registro de quem aprovou, quando, o valor antigo e o novo; desfazer quando a API deixar
- Permissão de escrita no app (os vendedores autorizam de novo) e mudança nos Termos e na Política, que hoje dizem
  que o Orzy só lê a conta

### Shopee e multicanal

Era a fase 9 até 18/10/2026 (a fase 7 até 17/10/2026 e a fase 4 até 15/10/2026).

- Shopee em todos os módulos: anúncios, pedidos, estoque e financeiro
- Estoque único entre os canais, usando a escrita das mudanças com aprovação

### Nota fiscal

Era a fase 10 até 18/10/2026.

- Emitir a NF-e das vendas por um emissor que já existe (o faturador do próprio Mercado Livre ou uma API de nota
  fiscal paga por nota). O Orzy não constrói emissor próprio: a nota muda com a reforma tributária até 2033
- Entrada das compras pelo XML da nota do fornecedor
- Aqui o Orzy passa a tratar dados dos compradores (nome, CPF e endereço): Política e Termos mudam e o advogado revisa
  antes. Cada vendedor precisa do próprio certificado digital A1
- Se os primeiros clientes pedirem nota fiscal antes, ela pode vir logo depois do lançamento

### Sem ordem definida

- Atendimento: perguntas e mensagens, com sugestão de resposta da Orzy Intelligence
- Aplicativo de celular e outros canais (Amazon, Magalu, loja própria)
