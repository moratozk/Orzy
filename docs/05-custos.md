# 05 · Custos

## Hoje

| Item | Custo |
|---|---|
| Python | Grátis |
| API do Mercado Livre | Grátis |
| Rodar no PC | Grátis, sem servidor |
| GitHub | Grátis |
| Domínio orzy.com.br | Comprado pelo Nicolas em 14/10/2026. Renova todo ano: não deixar vencer. |

## Fase 3 (site)

Hospedagem do site e do servidor que guarda o Client Secret. Existem opções grátis, com limites.

Estimativas de 15/10/2026, com US$ 1 = R$ 5,04 (cotação de 14/10/2026). Os preços mudam: conferir antes de contratar.

| Opção | R$ por mês (estimativa) |
|---|---|
| **Google: Cloud Run + Firestore em São Paulo** (recomendado pela thread "Hospedagem e domínio") | R$ 0 no teste (até 55 horas de servidor ligado no mês); até R$ 0,42 por hora além disso; teto de cerca de R$ 276. A porta de entrada no orzy.com.br pode somar cerca de R$ 92 |
| Render, plano pago de entrada + 1 GB de disco | cerca de R$ 37 (alternativa com valor fixo) |
| Hostinger VPS KVM 1 | de cerca de R$ 35 (promoção) a R$ 98 (preço cheio); precisa de alguém que cuide do Linux |
| Railway, plano Hobby + uso | de cerca de R$ 35 a R$ 100, conforme o uso |
| Oracle Cloud, Always Free | R$ 0, com riscos a validar (região e máquina ociosa) |

Nada foi contratado. Detalhes e fontes em [07-fase-3-plano.md](07-fase-3-plano.md).

## Fases 4 a 10 (ERP completo, aprovado em 17/10/2026)

Estimativas de 16/10/2026, com US$ 1 = R$ 5,04. Os preços do banco vêm de uma tabela de terceiros sem data: conferir
no site do Google antes de contratar. Fontes na proposta, em `/mnt/project-files/orzy/plano/erp-completo-proposta.md`
(seção 6).

| Item | Desde | Estimativa |
|---|---|---|
| Banco PostgreSQL no Cloud SQL em São Paulo, menor máquina (db-f1-micro) | Fase 4 | cerca de R$ 70 por mês com disco (uns US$ 12 só a máquina). Máquina compartilhada, sem garantia de disponibilidade do Google |
| Banco maior (db-g1-small) | Quando crescer | cerca de R$ 200 por mês com disco (uns US$ 38 só a máquina) |
| Servidor e agendador (Cloud Run) | Fase 4 | provavelmente R$ 0 no começo, pela cota grátis; calcular no plano da fase 4 |
| Orzy Intelligence | Fase 4 | por uso (regras abaixo); o custo por vendedor por mês vai no plano da fase 4 |
| Aviso por e-mail ou WhatsApp | Fase 4 | a decidir; o WhatsApp cobra por conversa |
| Emissor de nota fiscal | Fase 10 | por nota ou mensalidade; o faturador do próprio Mercado Livre é uma opção, com custo e quem pode usar a validar |
| Certificado digital A1 | Fase 10 | pago por cada vendedor, por ano; preço a confirmar |
| Cobrar dos vendedores | Antes da fase 5 | CNPJ, contador e meio de pagamento: custo do negócio, não do código |

A partir da fase 4 o Orzy tem custo fixo todo mês, mesmo sem vendedor pagante. Por isso a cobrança é decidida antes
da fase 5. O plano de cada fase traz a estimativa em reais por mês antes de qualquer contratação.

## Regras para qualquer custo novo

1. Avisar antes, com uma estimativa em reais por mês, e esperar o ok.
2. Preferir sempre a opção grátis que resolva.
3. Hospedagem ou servidor só a partir da fase 3, com o plano de custos aprovado.

## Orzy Intelligence, a IA do Orzy (quando existir o módulo)

Pedido do Nicolas (15/10/2026): a IA tem de ser "muito, mas muito eficiente" e o mais otimizada possível.

- Usar o modelo mais barato que resolva: **Haiku** para triagem e volume, **Sonnet** só para reescrita detalhada.
- Usar o modo **Batch** quando o resultado não for urgente (sai mais barato).
- Antes de rodar, mostrar o custo estimado da execução, com os preços do dia em anthropic.com/pricing.
- Mandar só o que a IA precisa: os anúncios que as regras já apontaram e só os campos usados.
- Não repetir trabalho: guardar a resposta e só pedir de novo quando o anúncio mudar. As instruções que se repetem
  em todo pedido vão com cache de prompt, que cobra menos pela parte repetida.
- Enquanto o módulo não existe, o Claude analisa os relatórios que o Nicolas colar na conversa, sem custo extra.
