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
- Pela documentação do Global Selling (developers em global-selling.mercadolibre.com/devsite/create-application):
  Usuários vem ativo em todo app e inclui a reputação do vendedor; Publicação e sincronização cobre anúncios, fotos,
  preços e visitas; Métricas do negócio cobre métricas de vendas, estoque e reputação, tendências e visitas;
  Vendas e envios cobre pedidos, envios, reclamações e devoluções. **[doc]**
- Depois de criado, o app aparece em Minhas aplicações só com o Client ID. O Secret fica em ⋮ > Editar, como
  "Chave secreta". A lista mostra "Aplicativo não certificado" e uma nota de "Configuração de segurança" (70 num app
  novo), que é recomendação. (visto em 14/10/2026)
- Trocar a senha ou tirar a permissão do app invalida tudo: tem que fazer login de novo. **[doc]**
- A Redirect URI tem que ser idêntica à cadastrada no app. **[doc]**
- Erros: `invalid_client` (Client ID ou Secret errado), `invalid_grant` (código ou refresh token vencido, já usado ou com Redirect URI diferente), `local_rate_limited` (429). **[doc]**

## Recursos

| Para quê | Chamada | Limites e observações |
|---|---|---|
| Quem está conectado | `GET /users/me` | Também confirma que o login funciona. |
| Lista de anúncios | `GET /users/{id}/items/search?status=active&limit=50&offset=N` | Paginação normal só até 1000 resultados. Acima disso: `search_type=scan` e depois `scroll_id` em cada chamada. **[doc]** |
| Detalhes dos anúncios | `GET /items?ids=A,B,C&attributes=id,title,...` | No máximo 20 IDs por chamada. Resposta: lista de `{code, body}`. O parâmetro `attributes` escolhe os campos. **[doc]** A fase 2 pede também `category_id`, `condition`, `listing_type_id` (`free` = Grátis, `gold_special` = Clássico, `gold_pro` = Premium), `pictures` (com `max_size`, ex.: `1200x900`), `attributes` (ficha técnica: `id`, `name`, `value_id`, `value_name`), `shipping.free_shipping` e `tags`. **[a validar]** |
| Limite do título da categoria | `GET /categories/{id}` | `settings.max_title_length` (o limite muda por categoria). **[doc]** |
| Campos da ficha técnica | `GET /categories/{id}/attributes` | Cada campo tem `id`, `name`, `relevance` e `tags`: `required` (obrigatório para publicar), `hidden`, `read_only`, `fixed`, `inferred` (o vendedor não preenche), `allow_variations` e `variation_attribute` (ficam nas variações). Campo marcado como "não se aplica": `value_id` "-1" e `value_name` vazio. Anúncio com a tag `incomplete_technical_specs` está perdendo exposição pela ficha. **[doc]** |
| Nota de qualidade | `GET /item/{id}/performance` (no singular) | `score` de 0 a 100, `level` (Bad, Average, Good) e `level_wording` (no Brasil: Básica, Satisfatória, Profissional). Em `buckets[].variables[].rules[]`, cada regra tem `status` (PENDING ou COMPLETED), `mode` (OPPORTUNITY ou WARNING) e `wordings.title`, o texto do que fazer. 404: a nota ainda não foi calculada. 401: quem pergunta não é o dono do anúncio. Substitui o `/items/{id}/health`, que vai ser desligado. **[doc, dezembro de 2025]** |
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
- [ ] Fase 2: o multiget devolve `pictures`, `attributes`, `shipping` e `tags` quando pedidos em `attributes=...`.
- [ ] Fase 2: `/item/{id}/performance` responde para anúncios do Brasil, com os textos em português e com a permissão de leitura que o app já tem.
- [ ] Fase 2: as fotos trazem `max_size` e a categoria traz `settings.max_title_length`.

## Fontes

- [Autenticação e autorização](https://developers.mercadolivre.com.br/en_us/authentication-and-authorization)
- [Gerenciar vendas (orders)](https://developers.mercadolivre.com.br/en_us/manage-sales)
- [Visitas](https://developers.mercadolibre.com.mx/en_us/visits-resource)
- [Itens e buscas](https://developers.mercadolivre.com.br/pt-br/itens-e-buscas)
- [Qualidade dos anúncios, com `/performance`](https://global-selling.mercadolibre.com/devsite/listings-quality-gs) (atualizada em 15/12/2025)
- [Qualidade dos anúncios, com o `/health` antigo](https://developers.mercadolibre.com.ar/en_us/listings-quality) (de 2022)
- [Atributos e tags da ficha técnica](https://developers.mercadolivre.com.br/en_us/attributes)
- [Fotos: tamanho recomendado e zoom](https://developers.mercadolibre.com.ar/en_us/working-with-pictures)
- [Boas práticas de título](https://developers.mercadolibre.com.ar/devsite/global-listing)
