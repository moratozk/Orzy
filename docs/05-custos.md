# 05 · Custos

## Hoje

| Item | Custo |
|---|---|
| Python | Grátis |
| API do Mercado Livre | Grátis |
| Rodar no PC | Grátis, sem servidor |
| GitHub | Grátis |
| Domínio orzy.com.br | Comprado pelo Nicolas em 14/10/2026. Renova todo ano: não deixar vencer. |

## Hospedagem do site base (estimativas de 15/10/2026)

Hospedagem do site e do servidor que guarda o Client Secret. Existem opções grátis, com limites. Desde 18/10/2026 o
site só vai ao ar com o sistema completo (fase 10); a thread "Hospedagem e domínio" refaz esta conta para o sistema
novo (PostgreSQL, tarefas em segundo plano e e-mail dos alertas).

Estimativas de 15/10/2026, com US$ 1 = R$ 5,04 (cotação de 14/10/2026). Os preços mudam: conferir antes de contratar.

| Opção | R$ por mês (estimativa) |
|---|---|
| **Google: Cloud Run + Firestore em São Paulo** (recomendado pela thread "Hospedagem e domínio") | R$ 0 no teste (até 55 horas de servidor ligado no mês); até R$ 0,42 por hora além disso; teto de cerca de R$ 276. A porta de entrada no orzy.com.br pode somar cerca de R$ 92 |
| Render, plano pago de entrada + 1 GB de disco | cerca de R$ 37 (alternativa com valor fixo) |
| Hostinger VPS KVM 1 | de cerca de R$ 35 (promoção) a R$ 98 (preço cheio); precisa de alguém que cuide do Linux |
| Railway, plano Hobby + uso | de cerca de R$ 35 a R$ 100, conforme o uso |
| Oracle Cloud, Always Free | R$ 0, com riscos a validar (região e máquina ociosa) |

Nada foi contratado. Detalhes e fontes em [07-fase-3-plano.md](07-fase-3-plano.md).

## Até o lançamento e no lançamento (ordem aprovada em 18/10/2026)

Estimativas de 17/10/2026, com US$ 1 = R$ 5,04 e os 14% de imposto do Google. Os preços mudam: conferir no site de
cada serviço antes de contratar. Detalhes e fontes em `/mnt/project-files/orzy/plano/nova-ordem-sistema-completo.md`
(seção 4); o banco do Google vem da proposta do ERP (`erp-completo-proposta.md`, seção 6), de uma tabela de terceiros.

| Etapa | Onde roda | Custo por mês |
|---|---|---|
| Construção (fases 4 a 8) | No ambiente do Claude e nos testes do GitHub, com Mercado Livre, IA e pagamento simulados; no PC do Nicolas, só um programa de conferência | R$ 0 |
| Testes com dados reais (do fim da fase 4 em diante) e demo do professor (fase 9) | Endereço de teste fechado no Cloud Run em São Paulo, banco PostgreSQL num plano grátis, e-mail dos alertas num plano grátis, IA de verdade, Mercado Pago no modo de teste | menos de R$ 1 no Google; banco R$ 0; IA em centavos por dia |
| Lançamento (fase 10) | orzy.com.br, banco pago e Mercado Pago de verdade | banco cerca de R$ 80 (Cloud SQL, menor máquina); porta de entrada R$ 0 ou cerca de R$ 105; 3,99% por pagamento; IA menos de R$ 1 por loja; advogado e contador a orçar |

Depois do lançamento:

| Item | Quando | Estimativa |
|---|---|---|
| Banco maior (db-g1-small) | Quando crescer | cerca de R$ 200 por mês com disco (uns US$ 38 só a máquina), sem o imposto |
| Aviso por WhatsApp | Se entrar | o WhatsApp cobra por conversa |
| Emissor de nota fiscal | Nota fiscal | por nota ou mensalidade; o faturador do próprio Mercado Livre é uma opção, com custo e quem pode usar a validar |
| Certificado digital A1 | Nota fiscal | pago por cada vendedor, por ano; preço a confirmar |

O endereço de teste pede o plano Blaze do Google, com cartão, e segue os avisos de gasto em R$ 5, R$ 10 e R$ 20 e a
trava de R$ 17 no servidor. A trava não vale para o banco: por isso ele fica num plano grátis (por exemplo o do Neon,
com 1 GB e 100 CU-horas por mês) até haver assinantes. O plano de cada fase traz a estimativa em reais por mês antes
de qualquer contratação.

## Regras para qualquer custo novo

1. Avisar antes, com uma estimativa em reais por mês, e esperar o ok.
2. Preferir sempre a opção grátis que resolva.
3. Servidor só no endereço de teste (fim da fase 4) e no lançamento, cada um com o custo aprovado antes.

## Orzy Intelligence, a IA do Orzy (quando existir o módulo)

Pedido do Nicolas (15/10/2026): a IA tem de ser "muito, mas muito eficiente" e o mais otimizada possível.

- Usar o modelo mais barato que resolva: **Haiku** para triagem e volume, **Sonnet** só para reescrita detalhada.
- Usar o modo **Batch** quando o resultado não for urgente (sai mais barato).
- Antes de rodar, mostrar o custo estimado da execução, com os preços do dia em anthropic.com/pricing. Em
  17/10/2026: Haiku 5.5 a US$ 0,10 por milhão de tokens de entrada e US$ 0,50 de saída, Sonnet 5.5 a US$ 2 e US$ 10,
  Batch pela metade. Uma análise de 20 anúncios sai por uns R$ 0,03 (R$ 0,013 com Batch); uma por dia fica abaixo de
  R$ 1 por loja por mês.
- A API da Anthropic é separada do plano do Claude do Nicolas e é pré-paga, em dólar: para quando o crédito acaba, e o
  Console tem um limite de gasto por mês. Nos testes automáticos a IA é simulada (R$ 0). A chave nunca vai para o chat
  nem para o Git.
- Mandar só o que a IA precisa: os anúncios que as regras já apontaram e só os campos usados.
- Não repetir trabalho: guardar a resposta e só pedir de novo quando o anúncio mudar. As instruções que se repetem
  em todo pedido vão com cache de prompt, que cobra menos pela parte repetida.
- Enquanto o módulo não existe, o Claude analisa os relatórios que o Nicolas colar na conversa, sem custo extra.
