# 01 · Visão geral

## O que é o Orzy

Um programa para vendedores do Mercado Livre (e depois da Shopee): se conecta à conta do vendedor,
mostra quais anúncios vendem e quais não vendem e sugere o que mudar em cada um para vender mais.

Hoje roda no PC. Na fase 3 vira um site em **orzy.com.br**, onde o vendedor só clica em "Conectar com Mercado Livre".
Começa como um MVP de custo zero e, aos poucos, vira um pequeno ERP para a loja.

Rumo (Plano de Desenvolvimento do Nicolas, 15/10/2026): três partes. Acompanhar os anúncios e guardar o histórico;
achar problemas e oportunidades e recomendar o que fazer, com regras e, depois, com a Orzy Intelligence (a IA do
Orzy); e o ERP, com custos e margem. Primeiro o Orzy observa, depois entende e recomenda, e só com autorização do
vendedor executa. A ordem está no [02-roadmap.md](02-roadmap.md).

## Para quem

- **Usuários:** vendedores do Mercado Livre que querem saber o que mudar nos próprios anúncios. Primeiro, pequenos
  vendedores, com dezenas ou centenas de anúncios.
- **Quem desenvolve:** Nicolas. Ele testa com a conta conectada no PC dele e, para ter mais números,
  com vendedores que autorizem o app.
- **Ambiente de desenvolvimento:** Windows, Prompt de Comando, Python 3.
- **Programação:** ele roda os comandos seguindo o passo a passo. Instruções precisam dizer exatamente o que digitar.

## Princípios

1. **Custo zero primeiro.** Até a fase 2 tudo roda no PC, sem servidor e sem serviço pago. O site da fase 3 tem custo
   de hospedagem. Qualquer custo novo é avisado antes, com estimativa.
2. **Só a biblioteca padrão do Python.** Nada de `pip install` enquanto der para evitar.
3. **Os dados ficam no PC até a fase 2.** Login e relatórios ficam na pasta do programa. `config.json` e `tokens.json`
   nunca vão para o GitHub nem para ninguém. No site, o cuidado com os dados dos vendedores (LGPD) entra no plano da fase 3.
4. **Mensagens em português, dizendo o que fazer.** Nada de erro técnico em inglês na tela.
5. **Testar antes com dados simulados**, e dizer o que ainda falta validar na conta real.
6. **Seguir o roadmap** ([02-roadmap.md](02-roadmap.md)). Fazer algo fora de ordem só depois de avisar o impacto.

## Onde está cada coisa

| Pasta / arquivo | O que é |
|---|---|
| `painel-ml/` | O programa do Mercado Livre. O passo a passo de uso está em `painel-ml/LEIA-ME.md`. |
| `testes/` | Mercado Livre simulado e testes automáticos. Não precisa de conta. |
| `docs/01` a `docs/07` | Plano do projeto. Para continuar o trabalho, comece pelo [06-status.md](06-status.md). |
