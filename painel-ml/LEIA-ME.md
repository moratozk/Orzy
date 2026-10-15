# Painel de anúncios do Mercado Livre (passo 1)

Conecta na sua conta do Mercado Livre e gera um relatório dos seus anúncios ativos com
**visitas, vendas e conversão** do período, a **nota de qualidade** que o Mercado Livre dá a cada um
e **o que mudar** em cada anúncio.
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

1. Entre em **developers.mercadolivre.com.br** com a sua conta do Mercado Livre (não precisa ser a conta
   com os anúncios) e vá em **Minhas aplicações > Criar nova aplicação**.
   - Se o site pedir, complete e valide os dados da sua conta primeiro: no Brasil isso é obrigatório para criar apps.
2. **Informações básicas:**
   - **Nome:** precisa ser único no Mercado Livre e ter pelo menos 5 caracteres (ex.: "Painel da Loja Tal").
   - **Nome curto:** o nome sem espaços e sem acento (ex.: `painellojatal`).
   - **Descrição:** até 150 caracteres. Ela aparece na tela em que o vendedor autoriza o app.
   - **Propósito** e **quantos usuários:** escolha o que for verdade para você. Para uso só seu: Pessoal e o menor intervalo.
   - **Logotipo:** o formulário exige uma imagem .png de até 1MB. Qualquer imagem serve para começar.
     Se ela for .jpg, abra no Paint e use **Arquivo > Salvar como > Imagem PNG**.
3. Na tela **Configuração e scopes**:
   - **URIs de redirect:** `https://www.google.com` (exatamente assim, sem barra no final).
   - **Fluxos OAuth:** deixe **Authorization Code** marcado e marque **Refresh Token**, que renova o login sozinho.
     Client Credentials pode ficar desmarcado: o painel não usa.
   - **PKCE:** pode marcar. Só lembre o que escolheu, porque o `conectar.py` vai perguntar.
   - **Negócios:** marque **Mercado Livre**.
   - **Permissões:** escolha **Leitura** em **Publicação e sincronização** (anúncios), **Métricas do negócio**
     (visitas) e **Venda e envios de um produto** (pedidos). Usuários fica como está (não dá para mudar)
     e o resto, Sem acesso.
   - **Tópicos e notificações:** não precisa marcar nada. Se o formulário exigir uma URL de
     notificação, use `https://www.google.com` também.
4. Salve. Para ver os dados do app, clique nos três pontinhos ⋮ ao lado dele e em **Editar**:
   o **Client ID** aparece como **ID do aplicativo** e o **Client Secret** como **Chave secreta**
   (clique no olhinho para ver). Não use a opção de renovar a chave: ela troca o Secret.
   A nota de "Configuração de segurança" na lista de apps é só uma recomendação.

## 2. Conecte sua conta

1. Abra esta pasta (`painel-ml`) no Explorador de Arquivos. Clique na barra de endereço, a faixa no alto
   da janela que mostra o caminho da pasta, aperte **Ctrl+A** e digite só `cmd`, de modo que a barra fique
   só com essa palavra. Aperte Enter: abre um Prompt de Comando (uma janela preta) já dentro da pasta.
   - Outro jeito, no Windows 11: clique com o botão direito num espaço vazio da pasta e escolha **Abrir no Terminal**.
2. Digite:

   ```
   python conectar.py
   ```

3. Ele pede o Client ID, o Client Secret, a Redirect URI (aperte Enter para usar o Google)
   e se você ativou o PKCE. Para colar, use Ctrl+V ou o botão direito do mouse. O Client Secret não aparece
   na tela depois de colado: é normal. Mesmo assim, não mande print dessa janela para ninguém.
4. O navegador abre no Mercado Livre. Entre com a conta **dona dos anúncios** e clique em **Permitir**.
   Se o navegador já estiver logado em outra conta, copie o link que o programa mostrou, abra numa janela
   anônima (Ctrl+Shift+N no Chrome ou no Edge) e faça este passo e o próximo nela.
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

Ele faz duas consultas por anúncio (visitas e nota de qualidade): numa conta com muitos anúncios, leva alguns minutos.
Depois mostra um resumo na tela e salva o **relatorio_anuncios.csv** nesta pasta, que abre direto no Excel.

Na tela aparecem quantos anúncios estão em cada situação, os que mais vendem e, em **Comece por estes**,
até 10 anúncios, dos que mais precisam de mudança para os que menos precisam. Cada um vem com até 3 sugestões e com
a nota de qualidade do Mercado Livre, quando ela existir. As outras sugestões ficam no CSV.

### O que tem no CSV

| Coluna | O que tem |
|---|---|
| situacao e o_que_olhar | Em que situação o anúncio está e o que costuma resolver (tabela abaixo). |
| o_que_mudar | As sugestões para este anúncio, numeradas da mais importante para a menos. |
| qualidade_ml | A nota que o Mercado Livre dá ao anúncio: Básica, Satisfatória ou Profissional, de 0 a 100. "ainda sem nota" quer dizer que ele ainda não calculou. |

### De onde vêm as sugestões

- **Título:** curto para o limite da categoria, palavras que o Mercado Livre pede para não usar (frete grátis,
  promoção, desconto, usado, lacrado...), estoque no título (pode fazer o anúncio ser moderado) e símbolos.
- **Fotos:** menos de 3, ou pequenas demais para ter zoom (o Mercado Livre recomenda 1200 x 1200 px).
- **Ficha técnica:** quantos campos da categoria estão preenchidos e quais faltam, os obrigatórios primeiro.
- **Frete grátis e tipo de anúncio (Grátis, Clássico, Premium):** como custam dinheiro, só aparecem
  para anúncios com problema de visita ou de venda.
- **Pedido do ML:** o que o próprio Mercado Livre pede para melhorar a nota de qualidade. Quando ele pede
  o mesmo que uma regra do Orzy, fica só o texto dele.

### O que cada situação quer dizer

| Situação | O que significa | Onde mexer |
|---|---|---|
| VISITA SEM VENDA | Muita gente vê, ninguém compra | Preço, fotos, frete, descrição |
| CONVERTE POUCO | Vende, mas pouco para as visitas que tem | Preço e frete comparados aos concorrentes |
| POUCA VISITA | Quase ninguém encontra | Título, palavras-chave, categoria, ficha técnica |
| VENDE, MAS POUCO VISTO | Quem vê, compra | Ganhar visitas: título melhor ou anúncio pago |
| VENDENDO BEM | Está funcionando | Use de modelo para os outros |

Os limites (30 visitas, 1% de conversão, 3 fotos e os outros) ficam no começo do `analise.py` e podem ser ajustados.
As visitas podem levar até 48 horas para aparecer no Mercado Livre.

---

## Deu erro?

- **"O Windows não pode localizar '...\painel-ml\cmd'"**: o `cmd` foi digitado no fim do caminho. Na barra de
  endereço, aperte Ctrl+A antes de digitar `cmd`, para a barra ficar só com essa palavra.
- **"python não é reconhecido"** ou **digitar `python` abre a Microsoft Store**: reinstale o Python
  marcando "Add python.exe to PATH", ou troque `python` por `py` nos comandos.
- **Erro de redirect_uri / URL de redirecionamento no navegador**: a Redirect URI do app e a que
  você digitou no programa precisam ser idênticas (atenção à barra no final).
  Rode `python conectar.py --refazer`.
- **"O código não foi aceito"**: ele vale poucos minutos e só pode ser usado uma vez.
  Rode `python conectar.py` de novo e cole o endereço logo depois de clicar em Permitir.
- **"Problema com o PKCE"**: rode `python conectar.py --refazer` e responda o PKCE igual ao que está no app.
- **"Sem permissão"**: entre com a conta dona dos anúncios, não com a de um operador. Se já entrou com ela,
  confira as permissões do app (passo 1, item 3) e rode `python conectar.py` de novo.
- **"Não consegui ler as visitas"**: quase sempre é o app sem permissão de métricas. Acerte no app
  e rode `python conectar.py` de novo.
- **"Não consegui ler a nota de qualidade"**: o relatório sai do mesmo jeito, só sem a nota. Se o erro disser
  "Sem permissão", confira as permissões do app (passo 1, item 3) e rode `python conectar.py` de novo.
- **"Não consegui ler a ficha técnica"**: o relatório sai sem as sugestões de ficha técnica. Tente de novo mais tarde.
- **"Sem conexão" ou "respondeu algo inesperado"**: confira a internet. Em rede com bloqueio, como a da
  escola ou do trabalho, o Mercado Livre pode estar bloqueado: tente de casa.
- **"Seu login venceu"**: rode `python conectar.py` de novo. Acontece se você trocar a senha,
  gerar um novo Secret no app ou ficar 6 meses sem usar.
- **O relatório não foi sobrescrito**: o CSV antigo estava aberto no Excel. O programa salva
  um novo com data e hora no nome.

## Segurança

`config.json` e `tokens.json` dão acesso à sua conta. Não envie para ninguém e não suba para o GitHub.
Se eles vazarem, gere um novo Client Secret no app do Mercado Livre e rode `python conectar.py --refazer`.
