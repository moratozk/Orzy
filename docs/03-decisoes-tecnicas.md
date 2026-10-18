# 03 · Decisões técnicas

Cada decisão com o motivo. Mudar alguma delas é uma conversa, não um detalhe.

| Decisão | Por quê |
|---|---|
| Python 3, só biblioteca padrão até a fase 3 | Instalar o Python é o único passo de instalação. Sem `pip`, sem versão quebrando. Na fase 4 o site passa para Django (ver abaixo). |
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
| Site no orzy.com.br, com um servidor guardando o Client Secret | O Orzy é para outros vendedores. Cada um criar o próprio app no Mercado Livre é difícil demais, e o Secret dentro de um programa distribuído pode ser copiado por qualquer um. Escolha do Nicolas em 14/10/2026. |
| O site só vai ao ar com o sistema completo (fase 10): conta, importação, alertas, Orzy Intelligence, ERP, planos e pagamento | Decisão do Nicolas em 17/10/2026; ordem aprovada em 18/10/2026, sem beta com vendedores convidados. Antes, os testes dele e uma conta demo para o professor dele (fase 9). |
| Endereço de teste fechado do fim da fase 4 em diante | Cada fase é conferida com os dados de verdade do Nicolas antes da próxima, sem mudar o orzy.com.br. Cloud Run em São Paulo, com os avisos de gasto em R$ 5, R$ 10 e R$ 20 e a trava de R$ 17 no servidor; liga só com o ok dele e o custo em reais. |
| Um app só, "OrzyApp", na conta do Nicolas | Serve para o teste e é editado no fim da fase 4 (endereço de teste) e no lançamento (Redirect URI do site e Client Secret novo), sempre com o ok do Nicolas. Só vira outro app se o Orzy passar para uma conta de empresa, que é o que o Mercado Livre recomenda para o dono da solução. |
| Alertas e comparações dizem o que mudou, sem afirmar a causa nem garantir resultado | Os dados mostram o que aconteceu, não o porquê. Do plano do Nicolas de 15/10/2026; os Termos (item 6) já dizem que as sugestões não garantem resultado. |
| Regras e contas ficam fora do modelo de IA sempre que der | Custo zero, resultado repetível e fácil de explicar. A Orzy Intelligence entra só onde regra não resolve. |
| Nenhuma mudança em anúncio sem aprovação do vendedor e sem registro (depois do lançamento) | Uma mudança errada custa dinheiro ao vendedor. O registro guarda quem aprovou, quando, o valor antigo e o novo. Vem depois de custos, margem e estoque (fases 5 e 6), para conferir antes de mudar preço ou estoque. |
| Django com PostgreSQL no começo da fase 4; Next.js e TypeScript do plano de 15/10/2026 ficam de fora | O ERP precisa de login com papéis, telas de cadastro e um banco relacional com histórico de mudanças. O Django traz isso pronto e continua em Python, então a coleta e as regras de `painel-ml/` entram sem reescrever; Next.js seriam duas linguagens para o Nicolas. Sem o beta, o Firestore do site base não chega a ser usado: o histórico vai direto para o PostgreSQL. Cada tabela leva o número da empresa, com testes de isolamento entre contas. Aprovado pelo Nicolas em 17/10/2026. |
| Banco PostgreSQL num plano grátis até o lançamento; banco pago (como o Cloud SQL em São Paulo, cerca de R$ 80 por mês com imposto) só no lançamento | A trava de gasto do Google só vale para o servidor, e o Cloud SQL passaria da regra do Nicolas de parar perto de R$ 20 por mês. Com uns 3 assinantes do Essencial o banco pago se paga. A thread "Hospedagem e domínio" escolhe o plano grátis e a de privacidade confere o contrato (LGPD). |
| Assinaturas pelo Mercado Pago (fase 8, a confirmar no plano da fase) | 3,99% por pagamento para receber em 30 dias, quem paga não precisa de conta no Mercado Pago e dá para testar de graça com usuários e cartões de teste; a Stripe sai mais cara. As credenciais nunca vão para o chat nem para o Git. |
| Login só pelo Mercado Livre até a fase 5 | Ninguém cria senha e o Orzy não guarda senha. Na fase 4 a conta Orzy é criada no clique em "Conectar com Mercado Livre"; na fase 5 entram o login com e-mail e senha e outros usuários da mesma empresa. |
| Refresh token guardado com criptografia e a chave fora do banco (fase 4) | Se o banco vazar, o acesso às contas dos vendedores não serve sem a chave. Até as mudanças com aprovação, depois do lançamento, o Orzy só lê as contas. |
| Fotos: o Orzy guarda só os links do Mercado Livre | As fotos já ficam nos servidores do Mercado Livre. Copiar custaria disco e tráfego, e os termos do Mercado Livre pedem apagar as cópias quando o vendedor sai. A regra de segurança do site que só mostra imagens próprias passa a liberar o endereço de imagens do Mercado Livre. |
| Permissão nova no OrzyApp só quando chega o módulo que usa | Pedir tudo no primeiro dia assusta quem conecta e vai contra a regra do plano do Nicolas de pedir só o necessário. Cada permissão nova faz o vendedor autorizar de novo. |
| Desconectar apaga os dados da conta, e o Orzy também apaga quando o vendedor tira a permissão no Mercado Livre (fase 4) | Os termos do Mercado Livre (item 14) pedem isso. |
| Sem nome, CPF e endereço do comprador até a nota fiscal (depois do lançamento), e nunca para a IA | Dados de compradores trazem obrigações da LGPD e risco de vazamento. A importação traz as vendas sem eles. |
| Nota fiscal só por um emissor que já existe (depois do lançamento) | Regras por estado, a reforma tributária mudando a nota até 2033, o certificado de cada vendedor e multa para o vendedor se a nota sair errada. |
