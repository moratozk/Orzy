# 07 · Fase 3: site no orzy.com.br (plano)

**Atualizado em:** 15/10/2026
**Situação:** planejamento e código em rascunho (PR aberto, sem merge). Nada foi contratado, publicado nem
mexido no app do Mercado Livre. Tudo depende das decisões do Nicolas, listadas no fim.

**Quem faz o quê:** ver [06-status.md](06-status.md). Deploy, DNS e textos legais ficam com as outras threads;
este arquivo cobre o código e as decisões. A pesquisa de hospedagem e LGPD está em
`/mnt/project-files/orzy/hospedagem-e-lgpd.md`.

## O que o site faz na primeira versão

- O vendedor clica em **Conectar com Mercado Livre** e entra com a própria conta. Ninguém cria app.
- O Client Secret do app fica só no servidor, numa variável de ambiente.
- Gera o relatório em segundo plano, com página de andamento. Quem fechar a página pode voltar depois.
- Mostra o resultado no navegador (o que mudar em cada anúncio primeiro) e baixa o mesmo CSV do PC.
- Guarda um histórico dos relatórios, para abrir cada um depois. Dá para apagar tudo com um clique.
- Tem página de privacidade (rascunho) e cabeçalhos de segurança.

Fica de fora: alterar anúncios, IA, Shopee, cobrança e cadastro com senha (o login é só pelo Mercado Livre).

## Plano em 5 passos (espera o ok do Nicolas)

1. **Hospedagem:** escolher uma opção da tabela de custos abaixo.
2. **App do Mercado Livre:** cadastrar a Redirect URI do site, gerar o Client Secret que vai só para o servidor e
   revisar os campos do formulário (quantos usuários, propósito). Isso muda o app, então só com o ok.
3. **Endereço de teste:** publicar num endereço temporário (não o orzy.com.br) e testar com a conta do Nicolas, um anúncio.
4. **Domínio e privacidade:** apontar o orzy.com.br para o site e revisar a política de privacidade com um advogado.
5. **Beta fechado:** 3 a 5 vendedores convidados, acompanhar erros; só depois aberto ao público.

## O que já está no código (PR de rascunho)

- `web/`: configuração, sessões na memória, login com PKCE, relatórios em segundo plano, histórico em SQLite,
  páginas, rotas e servidor (só biblioteca padrão do Python).
- `painel-ml/`: a mesma coleta e as mesmas regras do PC. O que mudou para o site: o login passou a ter uma
  versão que não grava em arquivo, e a coleta ganhou etapas e andamento que o PC também usa.
  O PC continua igual: os 64 testes antigos passam sem mudança.
- `testes/test_site.py`: 25 testes contra o Mercado Livre simulado. Cobrem o login inteiro, o estado do OAuth,
  o escape de títulos, o CSV com BOM, o isolamento entre contas, token vencido, pedido de outro site, histórico,
  cabeçalhos de segurança e uma ida e volta por HTTP real.
- Verificado: 89 testes passam no Python 3.13 e no 3.10 (64 do PC e 25 do site); pyflakes limpo; quebrar de
  propósito a checagem do estado ou o escape faz os testes falharem.

Limites da primeira versão (propostos, a confirmar):
- **Uma instância só**: as sessões e os relatórios em andamento ficam na memória do servidor.
- **Até 300 anúncios por relatório**, com aviso na tela quando passa disso.
- **Dois relatórios ao mesmo tempo** no servidor inteiro, e um por conta.
- **Histórico apagado após 365 dias** (feito automaticamente quando o servidor liga).
- **Sem refresh token**: quando o login vence (6 horas), a pessoa entra de novo.

Não testado ainda: o site falando com o Mercado Livre de verdade (depende da Redirect URI cadastrada, passo 2),
HTTPS e domínio, carga com muitos anúncios e a aparência em celular.

## Custos de hospedagem (estimativas de 15/10/2026)

Câmbio de referência: US$ 1 = R$ 5,04 (cotação de 14/10/2026, 10h45, renovainvest.com.br). Os preços mudam e
as páginas não mostravam a data: conferir na hora de contratar. Nada foi contratado.

| Opção | Estimativa (R$/mês) | Prós | Contras |
|---|---|---|---|
| **Render**, plano pago de entrada (US$ 7/mês, 512 MB de RAM) + disco persistente (US$ 0,25/GB/mês) | cerca de R$ 37 (com 1 GB de disco) | Sobe direto do GitHub; o Client Secret fica no painel do serviço; ninguém administra servidor | Servidores fora do Brasil; o plano grátis dorme e não tem disco garantido (a confirmar); 512 MB pode ser pouco para relatórios grandes (testar) |
| **Hostinger VPS KVM 1** (1 vCPU, 4 GB, 50 GB) | cerca de R$ 35 (promoção de US$ 6,99 no 1º ano) a R$ 98 (preço cheio de US$ 19,49) | Sempre ligado; controle total; o histórico fica no disco do servidor | Alguém precisa cuidar do Linux (atualizações, cópia de segurança); datacenter no Brasil não confirmado |
| **Railway**, plano Hobby (US$ 5/mês + uso de CPU e RAM) | estimativa de R$ 35 a R$ 100, conforme o uso real | Deploy simples; disco (volume) persistente | Cobra pelo uso: difícil prever o mês |
| **Oracle Cloud**, Always Free | R$ 0 | Sem custo | Região de São Paulo não confirmada; a Oracle pode desligar máquina ociosa (a validar); pede cartão |

**Recomendação:** Render para a primeira versão, porque o custo é previsível e não precisa administrar servidor.
A VPS é a alternativa mais barata no longo prazo, mas só se alguém (ele ou quem ele contratar) cuidar do Linux.

## Mercado Livre: o que o app precisa

1. **Redirect URI:** incluir a do site (`https://orzy.com.br/retorno`) e manter a do PC (`https://www.google.com`).
2. **Client Secret:** o Mercado Livre tem um só por app. Gerar um novo invalida o atual, então o PC precisa rodar
   `python conectar.py --refazer` de novo (com o segredo novo). O segredo do site fica só no painel de hospedagem.
   Isso segue a decisão de 14/10: um app só, o "OrzyApp".
3. **Quantos usuários e propósito:** a documentação não diz o efeito de cada resposta. Confirmar antes de abrir
   para vendedores de fora (a validar).
4. **Conta dona do app:** a pessoal do Nicolas serve para começar. Antes do público, vale avaliar uma conta de empresa
   (a validar na documentação).
5. **Termos de uso sobre guardar dados de vendedores:** a página não abriu hoje, nem em duas tentativas. Ler antes de abrir o site e confirmar se o histórico de 12 meses é permitido (a validar).

## LGPD (resumo, não é parecer jurídico)

Texto da Resolução CD/ANPD nº 2/2022, lido hoje:
- Agente de pequeno porte (ME, EPP, MEI, startup ou pessoa natural com fins econômicos) fica dispensado de
  indicar encarregado, mas precisa manter um canal de comunicação com quem tem os dados.
- Pode usar o registro de operações simplificado.
- Os prazos de atendimento e de comunicação de incidentes são dobrados, sem número fixo no texto: depende de
  norma específica da ANPD (a confirmar com advogado).
- O site não trata dados sensíveis. Por isso, em princípio, não cai no regime de alto risco. Confirmar.

O que o site guarda: o número e o apelido do vendedor (durante a sessão), e o histórico com títulos e números
dos anúncios. Tokens: só na memória. Dados de compradores: nenhum.

Antes de abrir ao público: política de privacidade revisada (rascunho em `/privacidade`), canal de contato,
responsável identificado, e uma conversa com advogado. Não tenho preço confiável de advogado: pedir orçamento.

## Decisões que o Nicolas precisa tomar

1. Hospedagem: Render (recomendado, ~R$ 37/mês), VPS Hostinger ou Railway.
2. Aprovar o passo 2 (mudança no app do Mercado Livre e novo Client Secret, com o PC rodando `--refazer`).
3. Limites da primeira versão: 300 anúncios por relatório, histórico por 12 meses, uma instância.
4. Nome e contato do responsável e um e-mail de contato para a política de privacidade.
5. Quando: beta fechado com 3 a 5 vendedores, ou direto ao público.
6. Revisão de advogado antes do público: sim ou não.

## Próximo passo

- Nicolas: responder os itens acima (uma palavra por item basta).
- Hospedagem e domínio (outra thread): com o ok do passo 1 e 2, publicar no endereço de teste. Nada de DNS,
  cobrança ou mudança no app sem o ok dele.
- Site (esta thread): ajustar o código conforme o teste real e integrar a página inicial quando chegar.
