# 03 · Decisões técnicas

Cada decisão com o motivo. Mudar alguma delas é uma conversa, não um detalhe.

| Decisão | Por quê |
|---|---|
| Python 3, só biblioteca padrão | Instalar o Python é o único passo de instalação. Sem `pip`, sem versão quebrando. |
| Roda no Prompt de Comando do Windows | É o ambiente do Nicolas. Os comandos no LEIA-ME são exatamente o que ele digita. |
| Redirect URI `https://www.google.com` | O Mercado Livre não aceita `localhost`. Depois do login, o código aparece no endereço do navegador e a pessoa cola no programa. |
| PKCE opcional, igual ao que está no app | O app pode ou não exigir PKCE. O `conectar.py` pergunta e segue o que foi configurado. |
| Login em `config.json` e `tokens.json` na pasta do programa | Fica só no PC. Os dois estão no `.gitignore` e nunca vão para o GitHub. |
| Refresh token salvo antes de qualquer outra coisa | Ele é de uso único: se o novo se perder, só fazendo login de novo. A gravação usa um arquivo `.tmp` e troca no final, para não corromper se o PC desligar. |
| Vendas = pedidos pagos em `/orders/search` | O `sold_quantity` do anúncio é o total da vida inteira, não do período. |
| Visitas = `/items/{id}/visits/time_window` | Uma chamada por anúncio, com o mesmo período do relatório. |
| No máximo 20 IDs por multiget e modo scan acima de 1000 anúncios | São limites da API (ver [04-api-mercado-livre.md](04-api-mercado-livre.md)). |
| Erro 429 e instabilidade: espera 2, 4 e 8 segundos e tenta de novo | É o que o Mercado Livre pede quando passa do limite de chamadas. Conexão que cai no meio também tenta de novo. |
| Limites da classificação: 30 visitas e 1% de conversão | Pontos de partida, ajustáveis no começo do `meus_anuncios.py`. Não são regras do Mercado Livre. |
| CSV com `;` e vírgula decimal, em UTF-8 com BOM | Abre direto no Excel em português, com acentos certos. |
| Se o CSV estiver aberto no Excel, salva outro com data e hora | O Windows não deixa sobrescrever arquivo aberto. |
| Todo erro vira mensagem em português com o que fazer | O Nicolas não deve ver erro técnico em inglês. |
| Testes com um Mercado Livre simulado (`testes/ml_simulado.py`) | Dá para testar tudo sem conta e sem internet. Também só biblioteca padrão. |
| Site no orzy.com.br na fase 3, com um servidor guardando o Client Secret | O Orzy é para outros vendedores. Cada um criar o próprio app no Mercado Livre é difícil demais, e o Secret dentro de um programa distribuído pode ser copiado por qualquer um. Escolha do Nicolas em 14/10/2026. |
| Um app só, "Orzy", na conta do Nicolas | Serve para o teste e é editado na fase 3 (Redirect URI do site e Client Secret novo). Só vira outro app se o Orzy passar para uma conta de empresa, que é o que o Mercado Livre recomenda para o dono da solução. |
