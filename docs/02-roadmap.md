# 02 · Roadmap

O Orzy é para vendedores do Mercado Livre (e depois da Shopee) analisarem os próprios anúncios.
O Nicolas desenvolve e testa com a conta conectada no PC dele e, para ter mais números,
com vendedores que autorizem o app.

Cada fase só começa quando a anterior estiver funcionando com dados reais.
Antes de escrever código grande numa fase, o plano dela (3 a 6 passos) é mostrado e espera o ok do Nicolas.

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

## Fase 3 · Site no orzy.com.br (planejamento e rascunho do código, sem publicar)

Decidido pelo Nicolas em 14/10/2026: é aqui que o Orzy vira site, para outros vendedores usarem sem instalar nada.
Plano em 5 passos, custos, LGPD e decisões em [07-fase-3-plano.md](07-fase-3-plano.md). O código está num PR de
rascunho: não entra no main nem vai para o ar antes do ok do Nicolas.

- O vendedor entra no orzy.com.br e clica em **Conectar com Mercado Livre**. Ninguém precisa criar app.
- Um servidor pequeno guarda o Client Secret do app do Orzy. O Secret nunca vai dentro de um programa distribuído.
- O app "OrzyApp" do teste é o mesmo: ganha o Redirect URI do site e um Client Secret novo, que só o servidor conhece.
- O relatório e as sugestões aparecem no navegador, no lugar do CSV.
- Cada relatório fica guardado, para ver se um anúncio melhorou depois de uma mudança. Esse histórico é a base do ERP.

Antes de começar, o plano da fase mostra:

- onde hospedar o site e o servidor, com o custo em reais por mês (existem opções grátis, com limites);
- como cuidar dos dados dos vendedores (LGPD e política de privacidade);
- se o app "OrzyApp" continua na conta do Nicolas ou passa para uma conta de empresa: o Mercado Livre recomenda
  criar o app na conta dona da solução, de preferência de empresa, para evitar problema de transferência depois.

## Fase 4 · Shopee

Conectar a conta da Shopee e trazer os mesmos números e sugestões, quando o Mercado Livre estiver redondo.

## Depois (sem ordem definida ainda)

- **Módulo de IA (opcional, pago):** reescrever título e descrição. Regras de custo em [05-custos.md](05-custos.md).
- **ERP:** estoque, custo e margem por anúncio, pedidos, contas a pagar e a receber.
