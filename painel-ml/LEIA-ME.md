# Painel de anúncios do Mercado Livre (passo 1)

Conecta na sua conta do Mercado Livre e gera um relatório dos seus anúncios ativos com
**visitas, vendas e conversão** do período, dizendo o que olhar em cada um.
Roda no seu computador, não precisa de servidor e não custa nada.

---

## Baixe o programa

1. Entre em **github.com/moratozk/Orzy** com a sua conta do GitHub.
2. Clique no botão verde **Code** e depois em **Download ZIP**.
3. Clique com o botão direito no arquivo baixado e escolha **Extrair tudo**.
4. Dentro da pasta extraída tem a pasta **painel-ml**. É nela que você vai trabalhar.

## 0. Instale o Python (só uma vez)

1. Entre em **python.org/downloads/windows** e, na versão mais nova (a primeira da lista),
   clique em **Windows installer (64-bit)**. Prefira esse instalador ao "Python install manager".
2. Na primeira tela da instalação, marque **"Add python.exe to PATH"** e clique em Install Now.
3. Para conferir: abra o Prompt de Comando e digite `python --version`. Tem que aparecer "Python 3...".

## 1. Crie o app no Mercado Livre

1. Entre em **developers.mercadolivre.com.br** com a conta **dona dos anúncios**
   e vá em **Minhas aplicações > Criar nova aplicação**.
   - Se o site pedir, complete e valide os dados da sua conta primeiro: no Brasil isso é obrigatório para criar apps.
2. **Nome, nome curto e descrição:** o que quiser (ex.: "Meu painel").
3. **Redirect URI:** `https://www.google.com` (exatamente assim, sem barra no final).
4. **PKCE:** se aparecer essa opção, pode ativar. Só lembre o que escolheu.
5. **Escopos / permissões:** marque **Leitura** (read) e **Acesso offline** (offline_access).
   Escrita pode ficar desmarcada por enquanto.
   - Se o formulário também mostrar permissões por área, marque pelo menos **leitura** nas áreas
     de anúncios (publicações), vendas (pedidos) e métricas (visitas). Os nomes podem variar um pouco no site.
6. **Tópicos e notificações:** não precisa marcar nada. Se o formulário exigir uma URL de
   notificação, use `https://www.google.com` também.
7. Salve. Na tela do app, copie o **Client ID** (o número) e o **Client Secret** (a chave).

## 2. Conecte sua conta

1. Abra esta pasta no Explorador de Arquivos, clique na barra de endereço, digite `cmd` e aperte Enter.
   Abre um Prompt de Comando já dentro da pasta.
2. Digite:

   ```
   python conectar.py
   ```

3. Ele pede o Client ID, o Client Secret, a Redirect URI (aperte Enter para usar o Google)
   e se você ativou o PKCE.
4. O navegador abre no Mercado Livre. Entre e clique em **Permitir**.
5. O navegador vai cair no Google com um endereço assim:
   `https://www.google.com/?code=TG-...&state=...`
   Copie esse endereço **inteiro** da barra do navegador e cole no Prompt. Faça logo, o código vence em poucos minutos.
6. Deve aparecer **"Pronto! Conectado como SEU_APELIDO"**. Isso só precisa ser feito uma vez:
   o login se renova sozinho.

## 3. Gere o relatório

```
python meus_anuncios.py
```

Para outro período: `python meus_anuncios.py --dias 60` (de 1 a 150 dias).

Ele mostra um resumo na tela e salva o **relatorio_anuncios.csv** nesta pasta, que abre direto no Excel.

### O que cada situação quer dizer

| Situação | O que significa | Onde mexer |
|---|---|---|
| VISITA SEM VENDA | Muita gente vê, ninguém compra | Preço, fotos, frete, descrição |
| CONVERTE POUCO | Vende, mas pouco para as visitas que tem | Preço e frete comparados aos concorrentes |
| POUCA VISITA | Quase ninguém encontra | Título, palavras-chave, categoria, ficha técnica |
| VENDE, MAS POUCO VISTO | Quem vê, compra | Ganhar visitas: título melhor ou anúncio pago |
| VENDENDO BEM | Está funcionando | Use de modelo para os outros |

Os limites (30 visitas e 1% de conversão) ficam no começo do `meus_anuncios.py` e podem ser ajustados.
As visitas podem levar até 48 horas para aparecer no Mercado Livre.

---

## Deu erro?

- **"python não é reconhecido"** ou **digitar `python` abre a Microsoft Store**: reinstale o Python
  marcando "Add python.exe to PATH", ou troque `python` por `py` nos comandos.
- **Erro de redirect_uri / URL de redirecionamento no navegador**: a Redirect URI do app e a que
  você digitou no programa precisam ser idênticas (atenção à barra no final).
  Rode `python conectar.py --refazer`.
- **"O código não foi aceito"**: ele vale poucos minutos e só pode ser usado uma vez.
  Rode `python conectar.py` de novo e cole o endereço logo depois de clicar em Permitir.
- **"Problema com o PKCE"**: rode `python conectar.py --refazer` e responda o PKCE igual ao que está no app.
- **"Sem permissão"**: entre com a conta dona dos anúncios, não com a de um operador. Se já entrou com ela,
  confira as permissões do app (passo 1, item 5) e rode `python conectar.py` de novo.
- **"Não consegui ler as visitas"**: quase sempre é o app sem permissão de métricas. Acerte no app
  e rode `python conectar.py` de novo.
- **"Sem conexão" ou "respondeu algo inesperado"**: confira a internet. Em rede com bloqueio, como a da
  escola ou do trabalho, o Mercado Livre pode estar bloqueado: tente de casa.
- **"Seu login venceu"**: rode `python conectar.py` de novo. Acontece se você trocar a senha,
  gerar um novo Secret no app ou ficar 6 meses sem usar.
- **O relatório não foi sobrescrito**: o CSV antigo estava aberto no Excel. O programa salva
  um novo com data e hora no nome.

## Segurança

`config.json` e `tokens.json` dão acesso à sua conta. Não envie para ninguém e não suba para o GitHub.
Se eles vazarem, gere um novo Client Secret no app do Mercado Livre e rode `python conectar.py --refazer`.
