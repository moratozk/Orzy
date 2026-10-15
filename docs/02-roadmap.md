# 02 · Roadmap

O Orzy é para vendedores do Mercado Livre (e depois da Shopee) analisarem os próprios anúncios.
O Nicolas desenvolve e testa com a conta conectada no PC dele e, para ter mais números,
com vendedores que autorizem o app.

Cada fase só começa quando a anterior estiver funcionando com dados reais.
Antes de escrever código grande numa fase, o plano dela (3 a 6 passos) é mostrado e espera o ok do Nicolas.

Rumo, do Plano de Desenvolvimento do Nicolas (15/10/2026), usado como referência e não como regra ("é só um plano
inicial"): primeiro o Orzy observa, depois entende e recomenda, e só com autorização do vendedor executa. A ordem das
fases 4 a 7 saiu desse plano e foi aprovada por ele em 15/10/2026. Texto do plano e comparação com este roadmap em
`/mnt/project-files/orzy/plano/`.

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
- [ ] Terminar o site base (aprovado em 15/10/2026):
  - [x] segurança das sessões
  - [x] páginas internas funcionando no celular
  - [x] comparação de relatórios no histórico (o que mudou em cada anúncio desde o relatório anterior)
  - [ ] histórico no Firestore
- [ ] Busca pelo título e filtro por situação na tabela "Todos os anúncios" (do plano de 15/10/2026)
- [ ] Identidade visual: logo, cores e letras (thread "Identidade visual e logo"). Depois que o Nicolas escolher uma
  direção, só a logo e as cores entram no site base
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

## Fase 4 · Alertas automáticos e Orzy Intelligence

Do plano do Nicolas (15/10/2026). O Orzy passa a olhar os anúncios sozinho, todo dia, e avisa o que mudou, sem o
vendedor precisar abrir o site. É o que o plano dele chama de primeira versão útil: conexão, histórico e alertas.

- Guardar no servidor, com criptografia, o acesso renovável (refresh token) de quem ativar os alertas. Hoje o site não
  guarda, e a Política de Privacidade diz isso: ela muda antes. O refresh token é de uso único, então só um processo
  por vendedor renova de cada vez, e o novo é salvo antes de qualquer outra coisa.
- Buscar os números todo dia e registrar as falhas (os termos do Mercado Livre pedem dados atualizados a cada 24 horas)
- Regras para quedas e oportunidades, comparando períodos equivalentes, sem afirmar a causa
- Ordenar por impacto e urgência, numa central de alertas no site (aviso por e-mail ou WhatsApp a decidir, com custo)
- Guardar cada recomendação e o que aconteceu depois; o vendedor marca se ajudou ou não
- **Orzy Intelligence (o módulo de IA, opcional, pago):** só onde regra não resolve: explicar os achados e sugerir
  título e descrição. Pedido do Nicolas (15/10/2026): tem de ser muito eficiente e o mais otimizada possível. Regras
  de custo e de otimização em [05-custos.md](05-custos.md). Até ela existir, as sugestões do relatório são
  regras fixas e o site não as chama de IA. Antes de ligar, a Política de Privacidade precisa dizer qual empresa faz a
  IA, em que país e com quais cláusulas da ANPD.

Antes de começar, o plano da fase mostra o custo em reais por mês (agendador, banco e IA).

## Fase 5 · ERP básico: custos e margem

- Produtos ligados aos anúncios, custo de compra, taxas e despesas
- Margem estimada por anúncio, vendas e faturamento, num painel com menu lateral
- Alerta de margem: avisar quando uma promoção ou o frete grátis pode comer o lucro
- "Empresa" com cadastro próprio, se precisar de mais de um usuário ou de mais de uma conta conectada (até lá, o
  login é só pelo Mercado Livre)

Antes de começar: rever a tecnologia (um framework Python e um banco relacional, como o PostgreSQL), com o motivo e o
custo em reais.

## Fase 6 · Executar mudanças com aprovação

- O vendedor revisa e aprova cada mudança antes; nada muda sozinho
- Alterar pelo Orzy o que a API do Mercado Livre deixa (preço, título, descrição e outros), conferindo limites e margem
- Registrar quem aprovou, quando, o valor antigo e o novo; desfazer quando a API deixar
- Precisa de permissão de escrita no app (os vendedores autorizam de novo) e de mudança nos Termos e na Política, que
  hoje dizem que o Orzy só lê a conta

## Fase 7 · Shopee

Conectar a conta da Shopee e trazer os mesmos números, sugestões e alertas, quando o Mercado Livre estiver redondo.
Era a fase 4 até 15/10/2026; o plano do Nicolas não fala da Shopee.

## Depois (sem ordem definida ainda)

- **Resto do ERP:** estoque, pedidos, contas a pagar e a receber.
- **Planos pagos:** por volume de anúncios, contas conectadas e recursos de IA, depois do beta e com os custos
  conhecidos.
