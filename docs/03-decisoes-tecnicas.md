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
| Limites da classificação: 30 visitas e 1% de conversão | Pontos de partida, ajustáveis no começo do `analise.py`. Não são regras do Mercado Livre. |
| Regras de situação e de sugestão no `analise.py`, separadas da coleta | O `meus_anuncios.py` busca os dados e o `analise.py` decide. O site da fase 3 usa as mesmas regras sem mexer nelas. |
| Regras de sugestão tiradas da documentação do Mercado Livre sempre que dá | Mínimo de 3 fotos, zoom acima de 800 px, o que não pôr no título e ficha técnica vêm das páginas do Mercado Livre. Os outros limites (título curto abaixo de 60% do limite, ficha com menos da metade preenchida) são pontos de partida. |
| Sugestões que custam dinheiro (frete grátis, Premium, sair do Grátis) só para anúncio com problema de visita ou de venda | Para um anúncio que já vende bem, o Orzy não manda gastar mais. |
| Nota de qualidade em `/item/{id}/performance` | A documentação do Mercado Livre (dezembro de 2025) avisa que o `/items/{id}/health` antigo vai ser desligado. |
| Quando o Mercado Livre pede o mesmo que uma regra do Orzy, fica o texto dele | É ele quem decide a exposição. A sugestão fica com o peso maior dos dois. |
| A nota de qualidade é um extra | Se ela não puder ser lida (sem permissão, erro), o relatório sai sem ela, com visitas, vendas e as outras sugestões. |
| CSV com `;` e vírgula decimal, em UTF-8 com BOM | Abre direto no Excel em português, com acentos certos. |
| Se o CSV estiver aberto no Excel, salva outro com data e hora | O Windows não deixa sobrescrever arquivo aberto. |
| Todo erro vira mensagem em português com o que fazer | O Nicolas não deve ver erro técnico em inglês. |
| Testes com um Mercado Livre simulado (`testes/ml_simulado.py`) | Dá para testar tudo sem conta e sem internet. Também só biblioteca padrão. |
| Site no orzy.com.br na fase 3, com um servidor guardando o Client Secret | O Orzy é para outros vendedores. Cada um criar o próprio app no Mercado Livre é difícil demais, e o Secret dentro de um programa distribuído pode ser copiado por qualquer um. Escolha do Nicolas em 14/10/2026. |
| Um app só, "OrzyApp", na conta do Nicolas | Serve para o teste e é editado na fase 3 (Redirect URI do site e Client Secret novo). Só vira outro app se o Orzy passar para uma conta de empresa, que é o que o Mercado Livre recomenda para o dono da solução. |
| Alertas e comparações dizem o que mudou, sem afirmar a causa nem garantir resultado | Os dados mostram o que aconteceu, não o porquê. Do plano do Nicolas de 15/10/2026; os Termos (item 6) já dizem que as sugestões não garantem resultado. |
| Regras e contas ficam fora do modelo de IA sempre que der | Custo zero, resultado repetível e fácil de explicar. A Orzy Intelligence entra só onde regra não resolve. |
| Nenhuma mudança em anúncio sem aprovação do vendedor e sem registro (fase 6) | Uma mudança errada custa dinheiro ao vendedor. O registro guarda quem aprovou, quando, o valor antigo e o novo. |
| Python continua; Next.js, TypeScript e PostgreSQL do plano de 15/10/2026 ficam para depois | O site já está em Python e usa a mesma coleta e as mesmas regras do PC. No começo da fase 5 (ERP), rever um framework Python e um banco relacional, com o motivo e o custo. |
| Login só pelo Mercado Livre até o ERP | Ninguém cria senha e o Orzy não guarda senha. "Empresa" com cadastro próprio só se a fase 5 precisar. |
