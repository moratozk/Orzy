# 06 · Status

**Atualizado em:** 14/10/2026
**Fase atual:** 1, painel do Mercado Livre funcionando ([02-roadmap.md](02-roadmap.md))

## Onde parou

O painel está no repositório e passou em todos os testes com o Mercado Livre simulado.
Ainda **não foi rodado na conta real**: o próximo passo é do Nicolas, em casa.

## Feito

- Código do painel em `painel-ml/` (veio de uma conversa anterior com o Claude, que não está acessível aqui).
- Mercado Livre simulado em `testes/ml_simulado.py` e 34 testes em `testes/test_painel.py`.
- Correções depois dos testes:
  - conexão que cai no meio da resposta fechava o programa com erro técnico em inglês: agora tenta de novo e, se não der, explica;
  - rede com bloqueio (escola, trabalho) que devolve uma página no lugar dos dados também fechava o programa: agora explica;
  - quando as visitas não podiam ser lidas (por exemplo, app sem permissão de métricas), o relatório saía todo "SEM DADOS" sem dizer por quê: agora mostra o motivo.
- LEIA-ME com como baixar do GitHub, permissões por área no app e os erros novos.
- Testes rodando sozinhos no GitHub a cada PR, no Windows (Python mais recente e 3.10) e no Linux: todos passam.

## O que foi testado (com dados simulados)

- Login com e sem PKCE, colando o endereço inteiro, só o código, ou o endereço sem `https://` e com aspas.
- Endereço de outra tentativa de login, código usado duas vezes, Secret errado, recusa no navegador.
- Renovação do login: token vencido, token recusado antes da hora, refresh token de uso único salvo na hora.
- Erro 429, conexão caindo, sem internet, rede com bloqueio, sem permissão.
- Relatório: as 5 situações, período de 30, 60 e acima de 150 dias, pedidos pagos x cancelados x não pagos,
  mais de 50 pedidos, até 1000 e mais de 1000 anúncios (modo scan), multiget de no máximo 20,
  CSV aberto no Excel, conta sem anúncios, login vencido no meio do relatório.
- Os dois programas rodando de verdade, como no Prompt de Comando, numa cópia da pasta.

## Falta validar na conta real

- [ ] Criar o app no Mercado Livre (formulário, permissões por área).
- [ ] `python conectar.py`: o Google mantém o código no endereço e o login dá certo.
- [ ] `python meus_anuncios.py`: roda sem erro e os números batem com o painel do Mercado Livre.
- [ ] Rodar no Windows de casa (os testes simulados já passam no Windows do GitHub).

## Próximo passo

Nicolas, no PC de casa, seguindo o `painel-ml/LEIA-ME.md`:

1. Instalar o Python.
2. Baixar o Orzy e abrir a pasta `painel-ml`.
3. Criar o app no Mercado Livre.
4. `python conectar.py`
5. `python meus_anuncios.py`
6. Mandar na conversa o que apareceu na tela, ou o erro. **Nunca** mandar o Client Secret, o `config.json` nem o `tokens.json`.

## Em aberto

- Quantos anúncios ativos a conta tem.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
