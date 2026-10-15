# 06 · Status

**Atualizado em:** 14/10/2026
**Fase atual:** 1, painel do Mercado Livre funcionando ([02-roadmap.md](02-roadmap.md))

## Onde parou

O painel está no repositório e passou em todos os testes com o Mercado Livre simulado.
O Nicolas está criando o app de teste no Mercado Livre. Ainda **não foi rodado com dados reais**.

## Decisões de 14/10/2026

- O Orzy é para outros vendedores analisarem os próprios anúncios. O Nicolas não tem conta com anúncios.
- O Nicolas comprou o domínio **orzy.com.br**.
- O Orzy vira site na **fase 3** (escolha do Nicolas). Até lá, o teste e a fase 2 seguem no programa do PC.
  Motivo: cada vendedor criar o próprio app é difícil demais, e o Client Secret não pode ir dentro de um programa distribuído.
- O app do Mercado Livre se chama "Orzy" e fica na conta do Nicolas. Ele serve para o teste e é editado na fase 3
  (Redirect URI do site), sem criar outro.

## Feito

- Código do painel em `painel-ml/` (veio de uma conversa anterior com o Claude, que não está acessível aqui).
- Mercado Livre simulado em `testes/ml_simulado.py` e 34 testes em `testes/test_painel.py`.
- Correções depois dos testes:
  - conexão que cai no meio da resposta fechava o programa com erro técnico em inglês: agora tenta de novo e, se não der, explica;
  - rede com bloqueio (escola, trabalho) que devolve uma página no lugar dos dados também fechava o programa: agora explica;
  - quando as visitas não podiam ser lidas (por exemplo, app sem permissão de métricas), o relatório saía todo "SEM DADOS" sem dizer por quê: agora mostra o motivo.
- LEIA-ME com como baixar do GitHub, permissões por área no app e os erros novos.
- LEIA-ME com os campos novos do formulário do app e como autorizar com outra conta numa janela anônima.
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

## Falta validar com dados reais

- [ ] Criar o app no Mercado Livre (formulário novo: propósito, quantos usuários e logotipo; permissões por área).
- [ ] `python conectar.py` com a conta do Nicolas: o Google mantém o código no endereço e o login dá certo.
- [ ] `python meus_anuncios.py` com a conta do Nicolas: diz "Nenhum anúncio ativo nessa conta." sem erro.
- [ ] Um vendedor com anúncios autoriza o app e os números batem com o painel do Mercado Livre.
- [ ] Rodar no Windows de casa (os testes simulados já passam no Windows do GitHub).

## Próximo passo

Nicolas, seguindo o `painel-ml/LEIA-ME.md`:

1. Instalar o Python.
2. Baixar o Orzy e abrir a pasta `painel-ml`.
3. Criar o app "Orzy" no Mercado Livre, com a conta dele.
4. `python conectar.py`, entrando com a conta dele.
5. `python meus_anuncios.py`. Com a conta dele, o esperado é "Nenhum anúncio ativo nessa conta.".
6. Para ver números, um vendedor conhecido autoriza o app: rodar `python conectar.py`, abrir o link que ele mostra
   numa janela anônima e deixar a pessoa entrar com a conta e a senha dela. Depois, `python meus_anuncios.py`.
7. Mandar na conversa o que apareceu na tela, ou o erro. **Nunca** mandar o Client Secret, o `config.json` nem o `tokens.json`.

## Em aberto

- Qual vendedor vai testar com anúncios reais.
- O que "propósito" e "quantos usuários" do formulário do app mudam: a documentação do Mercado Livre não fala.
- Se existirem os arquivos de plano originais da conversa anterior, juntar com estes.
