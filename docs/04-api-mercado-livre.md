# 04 · API do Mercado Livre

O que o painel usa, com os limites que importam. Base: `https://api.mercadolibre.com`.

Legenda: **[doc]** está na documentação oficial · **[código]** é como o painel faz, ainda não validado na conta real.

## Login (OAuth)

- Autorização (Brasil): `https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=...&redirect_uri=...&state=...` **[doc]**
- Com PKCE: mais `code_challenge` e `code_challenge_method=S256`. Se o app tiver PKCE ativado, mandar o challenge é obrigatório. **[doc]**
- Token: `POST /oauth/token` com corpo `application/x-www-form-urlencoded` **[doc]**
  - código: `grant_type=authorization_code`, `client_id`, `client_secret`, `code`, `redirect_uri` (e `code_verifier` com PKCE)
  - renovação: `grant_type=refresh_token`, `client_id`, `client_secret`, `refresh_token`
- O access token vale 6 horas (o exemplo da documentação mostra 3 horas, então o painel usa o `expires_in` da resposta). **[doc]**
- O refresh token é de uso único (cada renovação devolve um novo) e vence em 6 meses. Precisa do escopo `offline_access` **[doc]**,
  que no formulário novo do app aparece como o fluxo **Refresh Token**.
- Formulário novo do app (visto em 14/10/2026): nome único com pelo menos 5 caracteres, descrição de até 150 caracteres
  (aparece na autorização), propósito, quantos usuários e logotipo PNG obrigatório. Depois, na tela "Configuração e scopes":
  URIs de redirect, Fluxos OAuth (Authorization Code, Client Credentials, Refresh Token), PKCE, unidades de negócio
  (Mercado Livre, VIS) e permissões por área, cada uma com Sem acesso, Leitura ou Leitura e escrita: Usuários (fixo em
  Leitura e escrita), Comunicações pré e pós-vendas, Publicação e sincronização, Publicidade de um produto, Faturamento
  de uma venda, Métricas do negócio, Promoções, cupons e descontos de uma venda, Venda e envios de um produto.
  O painel pede Leitura em Publicação e sincronização (anúncios), Métricas do negócio (visitas) e Venda e envios
  de um produto (pedidos). **[código]**
- Trocar a senha ou tirar a permissão do app invalida tudo: tem que fazer login de novo. **[doc]**
- A Redirect URI tem que ser idêntica à cadastrada no app. **[doc]**
- Erros: `invalid_client` (Client ID ou Secret errado), `invalid_grant` (código ou refresh token vencido, já usado ou com Redirect URI diferente), `local_rate_limited` (429). **[doc]**

## Recursos

| Para quê | Chamada | Limites e observações |
|---|---|---|
| Quem está conectado | `GET /users/me` | Também confirma que o login funciona. |
| Lista de anúncios | `GET /users/{id}/items/search?status=active&limit=50&offset=N` | Paginação normal só até 1000 resultados. Acima disso: `search_type=scan` e depois `scroll_id` em cada chamada. **[doc]** |
| Detalhes dos anúncios | `GET /items?ids=A,B,C&attributes=id,title,...` | No máximo 20 IDs por chamada. Resposta: lista de `{code, body}`. |
| Visitas | `GET /items/{id}/visits/time_window?last=30&unit=day` | Campo `total_visits`. Período máximo de 150 dias. As visitas podem levar até 48 h para aparecer. **[doc]** |
| Vendas | `GET /orders/search?seller={id}&order.status=paid&order.date_created.from=...&order.date_created.to=...` | Datas no formato `2015-07-01T00:00:00.000-00:00`. Guarda só os últimos 12 meses. Pedidos cancelados não aparecem para o vendedor. **[doc]** |

## Limites e erros

- **429:** passou do limite de chamadas. Esperar alguns segundos e tentar de novo (o painel espera 2, 4 e 8 s). **[doc]**
- **401:** token recusado. O painel renova uma vez e, se não der, pede `python conectar.py`. **[código]**
- **403:** sem permissão. O painel sugere conferir se o login foi com a conta dona (não um operador) e se o app tem permissão de leitura para anúncios, vendas e métricas. **[código]**

## Ainda falta validar na conta real

- [ ] O Google mantém o `?code=...&state=...` no endereço depois do redirecionamento.
- [ ] Os nomes das permissões por área no formulário do app (anúncios, vendas, métricas).
- [ ] As respostas reais batem com os campos que o painel lê (`total_visits`, `order_items[].item.id`, `paging.total`).
- [ ] Os números do relatório batem com o painel do Mercado Livre no mesmo período.

## Fontes

- [Autenticação e autorização](https://developers.mercadolivre.com.br/en_us/authentication-and-authorization)
- [Gerenciar vendas (orders)](https://developers.mercadolivre.com.br/en_us/manage-sales)
- [Visitas](https://developers.mercadolibre.com.mx/en_us/visits-resource)
- [Itens e buscas](https://developers.mercadolivre.com.br/pt-br/itens-e-buscas)
