# Orzy

Programa para vendedores do Mercado Livre (e depois da Shopee): se conecta à conta do vendedor,
mostra quais anúncios vendem e quais não vendem e sugere o que mudar em cada um.
Hoje roda no PC. Está virando, módulo por módulo, um ERP completo com a Orzy Intelligence analisando os dados, e o
site em orzy.com.br só vai ao ar com tudo funcionando (fase 10).

## Por onde começar

- **Usar o painel:** siga o [painel-ml/LEIA-ME.md](painel-ml/LEIA-ME.md).
- **Ver o plano:** [docs/02-roadmap.md](docs/02-roadmap.md) e, para saber onde parou, [docs/06-status.md](docs/06-status.md).

## Pastas

| Pasta | O que tem |
|---|---|
| `painel-ml/` | O programa do Mercado Livre |
| `sistema/` | O sistema do Orzy em Django, com o site do orzy.com.br (fase 4, ainda sem publicar; ver [sistema/LEIA-ME.md](sistema/LEIA-ME.md)) |
| `testes/` | Mercado Livre simulado e os testes do programa do PC (os do sistema ficam em `sistema/testes/`) |
| `docs/` | Visão geral, roadmap, decisões técnicas, API, custos e status |

## Testes

Não precisam de conta nem de internet. Os do programa do PC, na pasta do Orzy, no Prompt de Comando:

```
python -m unittest discover -s testes -v
```

Os do sistema pedem o PostgreSQL: o passo a passo está no [sistema/LEIA-ME.md](sistema/LEIA-ME.md). O GitHub roda
os dois sozinho a cada PR (os do PC no Windows e no Linux).

## Segurança

`config.json` e `tokens.json` dão acesso à sua conta. Eles ficam só no seu PC e estão no `.gitignore`:
nunca suba esses arquivos para o GitHub.
