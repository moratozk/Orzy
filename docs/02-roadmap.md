# 02 · Roadmap

Cada fase só começa quando a anterior estiver funcionando na conta real.
Antes de escrever código grande numa fase, o plano dela (3 a 6 passos) é mostrado e espera o ok do Nicolas.

## Fase 1 · Painel do Mercado Livre funcionando (em andamento)

Conectar na conta e gerar o relatório de anúncios ativos com visitas, vendas e conversão,
separando os anúncios em 5 situações (visita sem venda, converte pouco, pouca visita,
vende mas pouco visto, vendendo bem).

- [x] Código do painel no repositório (`painel-ml/`)
- [x] Testes com Mercado Livre simulado (`testes/`)
- [ ] Criar o app no Mercado Livre e conectar a conta real
- [ ] Rodar o relatório na conta real e conferir os números com o painel do Mercado Livre

## Fase 2 · Sugestões de verdade para cada anúncio

Hoje o texto de "o que olhar" é igual para todos os anúncios da mesma situação.
Nesta fase o programa lê o próprio anúncio e diz o que mudar nele, usando só regras (custo zero):

- tamanho e conteúdo do título
- quantidade de fotos
- ficha técnica (atributos) incompleta
- frete grátis
- tipo de anúncio (clássico ou premium)
- a nota de qualidade que o próprio Mercado Livre dá ao anúncio, se a API mostrar

## Fase 3 · Tela no navegador e histórico

- Trocar o CSV por uma página que abre no navegador do PC.
- Guardar cada relatório num banco SQLite local, para ver se um anúncio melhorou depois de uma mudança.
- Esse histórico é a base do ERP.

## Fase 4 · Shopee

Conectar a conta da Shopee e trazer os mesmos números e sugestões, quando o Mercado Livre estiver redondo.

## Depois (sem ordem definida ainda)

- **Módulo de IA (opcional, pago):** reescrever título e descrição. Regras de custo em [05-custos.md](05-custos.md).
- **ERP:** estoque, custo e margem por anúncio, pedidos, contas a pagar e a receber.
