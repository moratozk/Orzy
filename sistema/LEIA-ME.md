# Sistema do Orzy (fase 4)

O sistema do Orzy em Django com PostgreSQL, já com o visual novo (o pacote da thread "Identidade visual e logo").
É a base da fase 4: faz o que o site base da fase 3 fazia (login com o Mercado Livre, relatório, histórico, textos
legais e contagens) e, desde o passo 2, guarda a conta com o acesso ao Mercado Livre cifrado. Os próximos passos da
fase entram aqui (importação completa, sincronia, alertas e Orzy Intelligence). Plano em [docs/02-roadmap.md](../docs/02-roadmap.md), fase 4.

Ainda não está publicado. Pela ordem aprovada pelo Nicolas, nada vai ao ar antes da fase 10. No fim da fase 4 o
sistema vai para um endereço de teste fechado, só para a conta dele, com o ok e o custo em reais antes.

## Como funciona

1. **Conectar com Mercado Livre:** `/entrar` manda o vendedor ao Mercado Livre, com PKCE e um estado conferido na
   volta. Em `/retorno`, o servidor troca o código pelo login usando o Client Secret e cria a conta no Orzy (ou
   atualiza a que já existe), sem senha. O token de acesso fica só na sessão, na memória do servidor. O código de
   renovação (refresh token) vai para o banco cifrado, com a chave fora dele (item 7). Nada vai para arquivo ou para
   o navegador: o único cookie do site é `orzy_sessao`.
2. **Gerar relatório:** roda em segundo plano, um por vez em cada conexão, com o anel de andamento
   (`/relatorio/<id>`).
3. **Resultado:** os números da conta, o que pede atenção, "Comece por estes" com o que mudar em cada anúncio e a
   tabela "Todos os anúncios", com busca pelo título e filtro por situação. Baixa o mesmo CSV do PC e diz a data e a
   hora em que os dados foram buscados (horário de Brasília).
4. **Histórico:** `/historico` abre no relatório guardado mais recente, com a linha do tempo dos outros. Cada um
   mostra o que mudou desde o anterior da mesma conta e do mesmo período, sem dizer por quê. Dá para apagar tudo,
   com confirmação. O que passa de 365 dias é apagado sozinho, uma vez por dia.
5. **Privacidade e Termos:** `/privacidade` e `/termos` mostram os textos de `docs/legal/`, lidos a cada pedido:
   mudar o texto não pede mudança no código. O rodapé de todas as páginas leva aos dois, e junto de cada botão
   Conectar aparece o aviso de que, ao conectar, a pessoa aceita os Termos.
6. **Contagens:** `/contagens` mostra quantos logins e relatórios (sem erro e com erro) o sistema teve por dia e
   quantos anúncios leu, sem dizer de quem, e quantas contas têm relatório guardado. Só abre para as contas de
   `ORZY_CONTAS_ADMIN`; para as outras, a página não existe (404), e nenhum link leva a ela.
7. **Acesso guardado** (`contas/acesso.py` e `contas/cofre.py`): o código de renovação é cifrado com AES-256-GCM, com
   a chave de `ORZY_CHAVE_ACESSO`. Ele é de uso único, então só um renova de cada vez em cada conta (a linha da conta
   fica travada no banco) e o novo é salvo antes de o token de acesso sair. Quando o token de acesso vence (6 horas),
   a sessão renova por aqui. Uma vez por dia o sistema renova as contas que não renovaram, para o código não vencer e
   para perceber quem tirou a permissão no Mercado Livre. Quando o Mercado Livre recusa o código (permissão tirada ou
   senha trocada), o acesso guardado sai na hora e as sessões da conta acabam; a conta e o histórico saem se a pessoa
   não conectar de novo em 30 dias.
8. **Sua conta:** `/conta`, pelo círculo com as iniciais no topo, mostra o que o Orzy guarda da conta e tem o
   "Desconectar e apagar tudo" (com confirmação): apaga a conta, o acesso guardado e o histórico, encerra as sessões
   da conta em todos os navegadores e tira a permissão do Orzy no Mercado Livre. Se o Mercado Livre não confirmar, o
   Orzy apaga do lado dele mesmo assim e avisa em `/conta/apagada`.

O sistema usa as mesmas regras e a mesma coleta do PC (`painel-ml/analise.py`, `painel-ml/meus_anuncios.py` e
`painel-ml/ml_api.py`), sem copiar código: `orzy/__init__.py` põe a pasta `painel-ml/` no caminho do Python.

## O que fica guardado no banco

Quatro tabelas (`contas/models.py` e `relatorios/models.py`). As três de relatório são o que a Política de
Privacidade diz (seção 6); a das contas é do passo 2 da fase 4 e ainda não está na Política: a thread "Privacidade e
termos" atualiza o texto antes de outra pessoa usar o sistema.

| Tabela | O que guarda |
|---|---|
| `Conta` | Uma por conta do Mercado Livre que conectou: o número e o apelido, quando entrou no Orzy, o último Conectar, o código de renovação cifrado (vazio quando não há acesso guardado), quando ele foi salvo e desde quando a conta está sem acesso |
| `RelatorioGuardado` | Um por relatório: a conta, a data, o período (dias), quantos anúncios e quantos em cada situação. Sai com a conta, pelo próprio banco |
| `AnuncioGuardado` | Um por anúncio do relatório: o número do anúncio (MLB...), o título, as visitas, as vendas, a situação e a pontuação das sugestões |
| `Contagem` | Um número por dia e por contagem (logins, relatórios sem erro, com erro e anúncios lidos), sem dizer de qual conta |

Nada de token de acesso, preço, estoque, link, e-mail ou dado de comprador; o código de renovação, só cifrado. As
sessões não têm tabela: ficam só na memória.

## Requisitos

- Python 3.12 ou mais novo (o Django 6 pede).
- PostgreSQL 16 (no Windows, o instalador de https://www.postgresql.org/download/windows/).
- As bibliotecas do `requirements.txt`, na pasta do Orzy: `python -m pip install -r requirements.txt`. O programa
  do PC (`painel-ml/`) continua sem nada para instalar.

## Variáveis de ambiente

| Variável | Obrigatória | Para que |
|---|---|---|
| `ORZY_ML_CLIENT_ID` | sim | Id do app no Mercado Livre |
| `ORZY_ML_CLIENT_SECRET` | sim | Client Secret do app. **Só no ambiente do servidor**, nunca no código ou no GitHub |
| `ORZY_URL_BASE` | sim | Endereço público do sistema, sem barra no fim. Precisa ser `https://` (para testar no computador: `http://127.0.0.1:porta`). O redirect do login é sempre esse endereço + `/retorno`, igual ao cadastrado no app, e todo pedido precisa chegar com esse endereço: os outros recebem 400 |
| `ORZY_BANCO_URL` | sim | O banco: `postgresql://usuário:senha@servidor:porta/banco`. Num banco de fora, com `?sslmode=require` no fim. A senha só no ambiente do servidor |
| `ORZY_CHAVE_ACESSO` | sim | A chave que abre o acesso guardado das contas: 32 bytes sorteados, em base64. Gere com `python -c "import secrets; print(secrets.token_urlsafe(32))"`. **Só no ambiente do servidor**, nunca junto do banco, no código ou no GitHub. Se ela mudar ou se perder, todo mundo precisa clicar em Conectar de novo (nenhuma conta é apagada por isso) |
| `ORZY_MAX_ANUNCIOS` | não | Quantos anúncios um relatório lê, no máximo (padrão: 300) |
| `ORZY_HORAS_SESSAO` | não | Quantas horas a sessão com login dura, contadas do login, mesmo em uso (padrão e máximo: 8, o que a Política promete). É também o prazo do cookie |
| `ORZY_CONTAS_ADMIN` | não | Números das contas do Mercado Livre que abrem `/contagens`, separados por vírgula. É o ID que o `conectar.py` do PC mostra em "Conectado como ... (ID ...)". Sem ela, ninguém abre |
| `PORT` e `ORZY_HOST` | não | Porta (padrão: 8000) e endereço (padrão: `0.0.0.0`) onde o gunicorn escuta. A hospedagem costuma definir `PORT` |

Sem uma das obrigatórias, o sistema não liga e diz o que falta.

## Como ligar no computador (Windows)

Só para ver as páginas: o Mercado Livre não aceita um endereço do próprio computador na volta do login, então o
login de verdade fica para o endereço de teste do fim da fase 4.

1. Instale o PostgreSQL. Na instalação, ele pede uma senha para o usuário `postgres`: anote.
2. Abra o **SQL Shell (psql)** do menu Iniciar, aperte Enter até ele pedir a senha, digite a senha do passo 1 e
   rode, trocando `UMA-SENHA` por uma senha sua, só com letras e números:

   ```
   CREATE USER orzy WITH PASSWORD 'UMA-SENHA' CREATEDB;
   CREATE DATABASE orzy OWNER orzy;
   ```

3. No Prompt de Comando, na pasta do Orzy (troque `UMA-SENHA` pela mesma do passo 2):

   ```
   python -m pip install -r requirements.txt
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   O último comando mostra uma chave (uma linha de letras, números, `-` e `_`). Copie e use no lugar de `A-CHAVE`:

   ```
   cd sistema
   set ORZY_ML_CLIENT_ID=1234567890
   set ORZY_ML_CLIENT_SECRET=qualquer-coisa
   set ORZY_URL_BASE=http://127.0.0.1:8000
   set ORZY_BANCO_URL=postgresql://orzy:UMA-SENHA@127.0.0.1:5432/orzy
   set ORZY_CHAVE_ACESSO=A-CHAVE
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py runserver 127.0.0.1:8000
   ```

4. Abra http://127.0.0.1:8000 no navegador. Para desligar, `Ctrl+C` no Prompt de Comando.

Os `set` valem só para aquela janela do Prompt de Comando. Não use o Client Secret de verdade no computador. Na
próxima vez, use a mesma chave em `ORZY_CHAVE_ACESSO`.

Na hospedagem, o servidor é o gunicorn (as opções estão em `gunicorn.conf.py`), ligado de dentro da pasta
`sistema/` depois do `migrate` e do `collectstatic`:

```
gunicorn orzy.wsgi
```

## Testes

Com o PostgreSQL ligado e as variáveis de cima (o usuário do banco precisa poder criar banco, o `CREATEDB` do passo
2), de dentro da pasta `sistema/`:

```
python manage.py test testes
```

O Django cria um banco só para os testes e apaga no fim. Os testes usam o Mercado Livre simulado
(`testes/ml_simulado.py`, o mesmo do PC) e não precisam de conta nem de internet. O GitHub roda esses testes sozinho a
cada PR, com um PostgreSQL só para o teste.

## Antes de publicar

No fim da fase 4, com a thread "Hospedagem e domínio", para o endereço de teste:

- **Um processo só.** As sessões com o login e os relatórios em andamento ficam na memória: o `gunicorn.conf.py` já
  liga um processo, e a hospedagem precisa de no máximo uma instância (no Cloud Run, máximo de instâncias = 1).
- **HTTPS na frente e o aviso do proxy.** A hospedagem entrega HTTPS e passa o pedido adiante: o Django precisa saber
  disso (`SECURE_PROXY_SSL_HEADER`, e `forwarded_allow_ips` no gunicorn) para depois ligar o HSTS
  (`SECURE_HSTS_SECONDS`). Hoje o `python manage.py check --deploy` só avisa do HSTS e do redirecionamento de http
  para https, que fica com a hospedagem.
- **Um proxy na frente que só repassa o pedido inteiro.** O servidor antigo cortava em 60 segundos uma conexão
  parada; o gunicorn não corta, e quem manda o pedido bem devagar prende uma das 8 linhas dele. A thread de
  hospedagem confere que a hospedagem escolhida faz isso (no Cloud Run, o Google recebe o pedido antes); num
  servidor próprio, entra um nginx na frente.
- **Conferência de saúde** por `/saude` com o endereço de `ORZY_URL_BASE`, ou só pela porta (o padrão do Cloud Run):
  com outro endereço, o sistema responde 400.
- **Registro em JSON, uma linha por evento,** para a hospedagem separar erro de aviso.
- **Uma linha à parte quando alguém apaga o histórico** (o número da conta e a hora, guardados 8 dias), para apagar de
  novo se uma cópia de segurança precisar ser restaurada. Pede antes uma frase na Política (thread "Privacidade e
  termos"); o plano está em `/mnt/project-files/orzy/hospedagem-monitoramento.md`.
- **O banco:** o PostgreSQL do plano grátis que a thread de hospedagem escolher, com o contrato conferido pela thread
  de privacidade (LGPD) antes de entrar dado de outra pessoa; `python manage.py migrate` antes de ligar.
- **`ORZY_CONTAS_ADMIN`** com o ID da conta do Nicolas no Mercado Livre, para ele abrir `/contagens`.
- **A chave do acesso guardado (`ORZY_CHAVE_ACESSO`)** gerada só para o servidor e guardada só no painel de segredos
  da hospedagem, nunca no mesmo lugar que o banco nem na cópia de segurança dele: quem tiver o banco sem a chave não
  abre o acesso das contas. A chave do computador não serve para o servidor.
- **O fluxo Refresh Token marcado no OrzyApp** (já está desde 14/10/2026): sem ele, a conta fica sem acesso guardado,
  e o registro avisa em cada Conectar.
- **A Política de Privacidade e os Termos com a conta guardada** (passo 2): a Política de hoje ainda diz que o acesso
  fica só na memória. A thread "Privacidade e termos" atualiza o texto, com o ok do Nicolas, antes de outra pessoa
  usar.
- **A Redirect URI do endereço de teste** cadastrada no OrzyApp, com o ok do Nicolas.
- **Client Secret, senha do banco e a chave do acesso guardado só no painel de segredos da hospedagem.** Nunca no
  código, no GitHub ou no `config.json` do PC.
- **Revisão de segurança completa** antes de qualquer outra pessoa entrar (fase 9), e a Política de Privacidade e os
  Termos de Uso completos (o que falta está em `docs/legal/LEIA-ME.md`).

## Arquivos

| Arquivo | O que faz |
|---|---|
| `manage.py` | Os comandos do Django (`migrate`, `collectstatic`, `runserver`, `test`) |
| `gunicorn.conf.py` | O servidor na hospedagem: um processo, a porta de `PORT` e uma linha de registro por pedido, sem IP e sem a busca |
| `orzy/settings.py` | Configuração do Django: banco, cookie, cabeçalhos de segurança, arquivos de `/static/` e registro |
| `orzy/configuracao.py` | Lê as variáveis de ambiente e avisa o que falta |
| `orzy/urls.py` | Os endereços do sistema e as páginas de erro |
| `orzy/wsgi.py` | Entrada do servidor; liga as limpezas em segundo plano |
| `orzy/seguranca.py` | `Cache-Control: no-store` nas páginas e os filtros do registro |
| `orzy/contexto.py` | O que toda página usa (e-mail de contato, apelido e iniciais da conta, aba aberta) |
| `orzy/testes.py` | Executor dos testes (junta os arquivos de `/static/` antes) |
| `contas/sessoes.py` | Sessões na memória, com prazo (8 horas depois do login, mesmo em uso; 15 minutos para quem não voltou do Mercado Livre), limite para as sem login e código novo depois do login |
| `contas/login.py` e `contas/views.py` | Entrar com o Mercado Livre (PKCE e conferência do estado), a volta, sair, a página "Sua conta" e o "Desconectar e apagar tudo" |
| `contas/models.py` | A tabela das contas |
| `contas/cofre.py` | Cifra e abre o código de renovação (AES-256-GCM, com a chave de `ORZY_CHAVE_ACESSO`) |
| `contas/acesso.py` | O acesso guardado: salvar no Conectar, renovar um de cada vez, perder quando o Mercado Livre recusa, a conferência de todo dia, as contas sem acesso há 30 dias e apagar tudo |
| `relatorios/geracao.py` | Gera o relatório em segundo plano e guarda o andamento |
| `relatorios/models.py` e `relatorios/historico.py` | O histórico e as contagens no PostgreSQL: salvar, listar, ver, achar o anterior, apagar e apagar os antigos |
| `relatorios/comparacao.py` | O que mudou entre dois relatórios do histórico (mesma conta e mesmo período) |
| `relatorios/busca.py` | Busca pelo título e filtro por situação em "Todos os anúncios" |
| `relatorios/contagens.py` | O que se conta por dia, sem dizer de quem, e o resumo da página `/contagens` |
| `relatorios/limpezas.py` | Apaga o histórico e as contagens com mais de 365 dias todo dia, confere as contas todo dia e apaga as sessões vencidas a cada minuto |
| `relatorios/telas.py`, `relatorios/formatos.py` e `relatorios/datas.py` | O que cada tela mostra, os números e as datas no formato brasileiro e o horário de Brasília |
| `relatorios/views.py` | As páginas do relatório, do histórico e das contagens |
| `publico/legal.py` | Mostra a Política de Privacidade e os Termos a partir do Markdown de `docs/legal/`, com escape |
| `publico/views.py` e `publico/paginas.py` | Página inicial, textos legais, `robots.txt`, `/saude` e as páginas de erro |
| `*/templates/` | O HTML das páginas, do pacote visual (todo texto do Mercado Livre passa por escape) |
| `publico/static/` | Estilos, scripts, ícones e as fontes Geist e Unbounded (licenças em `OFL-Geist.txt` e `OFL-Unbounded.txt`) |
| `testes/` | Os testes do sistema, contra o Mercado Livre simulado |
