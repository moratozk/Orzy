# Site do Orzy (fase 3)

Site para o vendedor entrar com a conta do Mercado Livre e ver o relatório no navegador. Ainda não está publicado.
O visual de agora é uma base: o final vem com a identidade visual do Orzy (ordem em
[docs/02-roadmap.md](../docs/02-roadmap.md), fase 3).
Plano, custos e decisões em [docs/07-fase-3-plano.md](../docs/07-fase-3-plano.md).

## Como funciona

1. **Conectar com Mercado Livre:** o vendedor é mandado ao Mercado Livre, autoriza, e volta para `/retorno`.
   O servidor troca o código pelo login usando o Client Secret (PKCE também). O login fica na sessão, na memória.
2. **Gerar relatório:** roda em segundo plano, com página de andamento (`/relatorio/<id>`).
3. **Resultado:** o mesmo conteúdo do CSV do PC, com "Comece por estes" e a tabela de todos os anúncios, e a data e
   a hora em que os dados foram buscados (horário de Brasília).
4. **Histórico:** cada relatório fica guardado (só números e títulos); dá para abrir e apagar tudo. O que passa de
   365 dias é apagado sozinho: o servidor confere ao ligar e depois uma vez por dia.
5. **Privacidade e Termos:** `/privacidade` e `/termos` mostram os textos de `docs/legal/`, que são de outra frente do
   projeto. O site lê o arquivo a cada pedido: mudar o texto não pede mudança no código. O rodapé de todas as páginas
   leva aos dois, e junto de cada botão Conectar aparece o aviso de que, ao conectar, a pessoa aceita os Termos.

O site usa as mesmas regras e a mesma coleta do PC (`painel-ml/analise.py` e `painel-ml/meus_anuncios.py`).

## Requisitos

- Python 3.10 ou mais novo. Só biblioteca padrão: não precisa de `pip install`.

## Variáveis de ambiente

| Variável | Obrigatória | Para que |
|---|---|---|
| `ORZY_ML_CLIENT_ID` | sim | Id do app no Mercado Livre |
| `ORZY_ML_CLIENT_SECRET` | sim | Client Secret do app. **Só no ambiente do servidor**, nunca no código ou no GitHub |
| `ORZY_URL_BASE` | sim | Endereço público do site, sem barra no fim. Precisa ser `https://` (para testar aqui: `http://127.0.0.1:porta`) |
| `ORZY_BANCO` | não | Arquivo SQLite do histórico (padrão: `orzy.db`). Na hospedagem, num disco que não some ao reiniciar |
| `ORZY_HOST` | não | Endereço onde o servidor escuta (padrão: `127.0.0.1`). Na hospedagem, `0.0.0.0` |
| `PORT` ou `ORZY_PORTA` | não | Porta (padrão: 8000). A hospedagem costuma definir `PORT` |
| `ORZY_MAX_ANUNCIOS` | não | Quantos anúncios um relatório lê, no máximo (padrão: 300) |
| `ORZY_HORAS_SESSAO` | não | Depois de quantas horas sem uso a sessão some (padrão: 8) |

O redirect do login é sempre `ORZY_URL_BASE` + `/retorno`. Ele precisa ser igual ao cadastrado no app do Mercado Livre.

## Como ligar

Na pasta do Orzy, com as variáveis definidas:

```
python -m web.servidor
```

Sem `ORZY_ML_CLIENT_ID`, `ORZY_ML_CLIENT_SECRET` ou `ORZY_URL_BASE`, o programa para e diz o que falta.

## Testes

```
python -m unittest discover -s testes -v
```

Os testes do site (`testes/test_site.py`) usam o Mercado Livre simulado e não precisam de conta nem de internet.

## Antes de publicar

- **Uma instância só.** Sessões e relatórios em andamento ficam na memória do servidor.
- **Banco em disco persistente** (`ORZY_BANCO`). No Cloud Run, a hospedagem recomendada, o disco apaga a cada
  reinício: o histórico vai para o Firestore, uma das mudanças listadas em `docs/07-fase-3-plano.md`.
- **HTTPS na frente** (a hospedagem resolve), e a Redirect URI do site cadastrada no app.
- **Política de Privacidade e Termos de Uso completos** (rascunhos em `docs/legal/`; o que falta preencher está em
  `docs/legal/LEIA-ME.md`) e canal de contato definido.
- **Client Secret só no painel de variáveis da hospedagem.** Nunca no código, no GitHub ou no `config.json` do PC.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `configuracao.py` | Lê as variáveis de ambiente e avisa o que falta |
| `login.py` | Entrar com o Mercado Livre (PKCE e conferência do estado) |
| `sessoes.py` | Sessões na memória, com prazo (8 horas com login, 15 minutos sem), limite para as sem login e código novo depois do login |
| `relatorios.py` | Gera o relatório em segundo plano e guarda o andamento |
| `historico.py` | Histórico em SQLite: salvar, listar, ver, apagar e apagar os antigos |
| `paginas.py` | HTML das páginas (todo texto do Mercado Livre passa por escape) |
| `legal.py` | Mostra a Política de Privacidade e os Termos de Uso a partir do Markdown de `docs/legal/`, com escape |
| `app.py` | Rotas, cookies, cabeçalhos de segurança e conferência da origem dos pedidos |
| `servidor.py` | Liga o servidor HTTP, não registra a busca (`?code=...`) no log, fecha conexões paradas depois de 60 segundos e apaga o histórico antigo todo dia |
| `static/` | Folha de estilo e o script da página de andamento |
