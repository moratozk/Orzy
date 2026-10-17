# Orzy

Programa para vendedores do Mercado Livre (e depois da Shopee): se conecta à conta do vendedor,
mostra quais anúncios vendem e quais não vendem e sugere o que mudar em cada um.
Hoje roda no PC; na fase 3 vira um site em orzy.com.br.
Começa com custo zero e vai virar, módulo por módulo, um ERP completo com a Orzy Intelligence analisando os dados.

## Por onde começar

- **Usar o painel:** siga o [painel-ml/LEIA-ME.md](painel-ml/LEIA-ME.md).
- **Ver o plano:** [docs/02-roadmap.md](docs/02-roadmap.md) e, para saber onde parou, [docs/06-status.md](docs/06-status.md).

## Pastas

| Pasta | O que tem |
|---|---|
| `painel-ml/` | O programa do Mercado Livre |
| `web/` | O site do orzy.com.br (fase 3, ainda sem publicar; ver [web/LEIA-ME.md](web/LEIA-ME.md)) |
| `testes/` | Mercado Livre simulado e testes automáticos |
| `docs/` | Visão geral, roadmap, decisões técnicas, API, custos e status |

## Testes

Não precisam de conta nem de internet. Na pasta do Orzy, no Prompt de Comando:

```
python -m unittest discover -s testes -v
```

O GitHub também roda esses testes sozinho a cada PR, no Windows e no Linux.

## Segurança

`config.json` e `tokens.json` dão acesso à sua conta. Eles ficam só no seu PC e estão no `.gitignore`:
nunca suba esses arquivos para o GitHub.
