# 01 · Visão geral

## O que é o Orzy

Um programa que roda no PC do Nicolas, se conecta à conta dele no Mercado Livre (e depois na Shopee),
mostra quais anúncios vendem e quais não vendem e sugere o que mudar em cada um para vender mais.

Começa como um MVP de custo zero e, aos poucos, vira um pequeno ERP para a loja.

## Para quem

- **Usuário:** Nicolas, vendedor no Mercado Livre.
- **Ambiente:** Windows, Prompt de Comando, Python 3.
- **Programação:** ele roda os comandos seguindo o passo a passo. Instruções precisam dizer exatamente o que digitar.

## Princípios

1. **Custo zero primeiro.** Tudo roda no PC, sem servidor e sem serviço pago. Qualquer custo novo é avisado antes, com estimativa.
2. **Só a biblioteca padrão do Python.** Nada de `pip install` enquanto der para evitar.
3. **Os dados ficam no PC.** Login e relatórios ficam na pasta do programa. `config.json` e `tokens.json` nunca vão para o GitHub nem para ninguém.
4. **Mensagens em português, dizendo o que fazer.** Nada de erro técnico em inglês na tela.
5. **Testar antes com dados simulados**, e dizer o que ainda falta validar na conta real.
6. **Seguir o roadmap** ([02-roadmap.md](02-roadmap.md)). Fazer algo fora de ordem só depois de avisar o impacto.

## Onde está cada coisa

| Pasta / arquivo | O que é |
|---|---|
| `painel-ml/` | O programa do Mercado Livre. O passo a passo de uso está em `painel-ml/LEIA-ME.md`. |
| `testes/` | Mercado Livre simulado e testes automáticos. Não precisa de conta. |
| `docs/01` a `docs/06` | Plano do projeto. Para continuar o trabalho, comece pelo [06-status.md](06-status.md). |
