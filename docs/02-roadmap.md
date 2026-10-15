# 02 · Roadmap

O Orzy é para vendedores do Mercado Livre (e depois da Shopee) analisarem os próprios anúncios.
O Nicolas desenvolve, mas não tem conta com anúncios: o login é testado com a conta dele e os números,
com um vendedor que autoriza o app.

Cada fase só começa quando a anterior estiver funcionando com dados reais.
Antes de escrever código grande numa fase, o plano dela (3 a 6 passos) é mostrado e espera o ok do Nicolas.

## Fase 1 · Painel do Mercado Livre funcionando (em andamento)

Conectar na conta e gerar o relatório de anúncios ativos com visitas, vendas e conversão,
separando os anúncios em 5 situações (visita sem venda, converte pouco, pouca visita,
vende mas pouco visto, vendendo bem).

- [x] Código do painel no repositório (`painel-ml/`)
- [x] Testes com Mercado Livre simulado (`testes/`)
- [ ] Criar o app "Orzy" no Mercado Livre, na conta do Nicolas, e conectar
- [ ] Rodar o relatório na conta de um vendedor que autorize o app e conferir os números com o painel do Mercado Livre

## Fase 2 · Sugestões de verdade para cada anúncio

Hoje o texto de "o que olhar" é igual para todos os anúncios da mesma situação.
Nesta fase o programa lê o próprio anúncio e diz o que mudar nele, usando só regras (custo zero):

- tamanho e conteúdo do título
- quantidade de fotos
- ficha técnica (atributos) incompleta
- frete grátis
- tipo de anúncio (clássico ou premium)
- a nota de qualidade que o próprio Mercado Livre dá ao anúncio, se a API mostrar

A análise fica separada do CSV, para ser usada do mesmo jeito no site da fase 3.

## Fase 3 · Site no orzy.com.br

Decidido pelo Nicolas em 14/10/2026: é aqui que o Orzy vira site, para outros vendedores usarem sem instalar nada.

- O vendedor entra no orzy.com.br e clica em **Conectar com Mercado Livre**. Ninguém precisa criar app.
- Um servidor pequeno guarda o Client Secret do app do Orzy. O Secret nunca vai dentro de um programa distribuído.
- O app "Orzy" do teste é o mesmo: ganha o Redirect URI do site e um Client Secret novo, que só o servidor conhece.
- O relatório e as sugestões aparecem no navegador, no lugar do CSV.
- Cada relatório fica guardado, para ver se um anúncio melhorou depois de uma mudança. Esse histórico é a base do ERP.

Antes de começar, o plano da fase mostra:

- onde hospedar o site e o servidor, com o custo em reais por mês (existem opções grátis, com limites);
- como cuidar dos dados dos vendedores (LGPD e política de privacidade);
- se o app "Orzy" continua na conta do Nicolas ou passa para uma conta de empresa: o Mercado Livre recomenda
  criar o app na conta dona da solução, de preferência de empresa, para evitar problema de transferência depois.

## Fase 4 · Shopee

Conectar a conta da Shopee e trazer os mesmos números e sugestões, quando o Mercado Livre estiver redondo.

## Depois (sem ordem definida ainda)

- **Módulo de IA (opcional, pago):** reescrever título e descrição. Regras de custo em [05-custos.md](05-custos.md).
- **ERP:** estoque, custo e margem por anúncio, pedidos, contas a pagar e a receber.
