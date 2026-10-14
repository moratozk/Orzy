# Orzy

Programa que roda no seu PC, se conecta à sua conta do Mercado Livre (e depois à Shopee),
mostra quais anúncios vendem e quais não vendem e sugere o que mudar em cada um.
Começa com custo zero e vai virar um pequeno ERP.

## Por onde começar

- **Usar o painel:** siga o [painel-ml/LEIA-ME.md](painel-ml/LEIA-ME.md).
- **Ver o plano:** [docs/02-roadmap.md](docs/02-roadmap.md) e, para saber onde parou, [docs/06-status.md](docs/06-status.md).

## Pastas

| Pasta | O que tem |
|---|---|
| `painel-ml/` | O programa do Mercado Livre |
| `testes/` | Mercado Livre simulado e testes automáticos |
| `docs/` | Visão geral, roadmap, decisões técnicas, API, custos e status |

## Testes

Não precisam de conta nem de internet. Na pasta do Orzy, no Prompt de Comando:

```
python -m unittest discover -s testes -v
```

## Segurança

`config.json` e `tokens.json` dão acesso à sua conta. Eles ficam só no seu PC e estão no `.gitignore`:
nunca suba esses arquivos para o GitHub.
