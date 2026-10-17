"""
Passo 2: lista seus anúncios ativos com visitas, vendas e conversão do período,
a nota de qualidade que o Mercado Livre dá a cada um e o que mudar em cada anúncio.

Como usar (no Prompt de Comando, dentro desta pasta):
    python meus_anuncios.py             últimos 30 dias
    python meus_anuncios.py --dias 60   outro período (1 a 150 dias)

Gera o arquivo relatorio_anuncios.csv, que abre direto no Excel.
As regras das situações e das sugestões ficam no analise.py.
"""

import argparse
import csv
import io
import sys
import textwrap
import time
from datetime import datetime, timedelta, timezone

import analise
import ml_api

PAUSA_ENTRE_CHAMADAS = 0.05
SUGESTOES_NA_TELA = 3  # as outras ficam no CSV

# O que o relatório pede de cada anúncio: os números e o que as sugestões precisam olhar.
CAMPOS_DOS_ANUNCIOS = ("id,title,price,currency_id,available_quantity,status,permalink,"
                       "category_id,condition,listing_type_id,pictures,attributes,shipping,tags")

ARQ_RELATORIO = ml_api.PASTA / "relatorio_anuncios.csv"


# ---------------------------------------------------------------- coleta

def listar_ids_ativos(cliente, user_id):
    caminho = f"/users/{user_id}/items/search"
    primeira = cliente.get(caminho, {"status": "active", "limit": 50, "offset": 0}) or {}
    total = (primeira.get("paging") or {}).get("total", 0)
    ids = list(primeira.get("results") or [])

    if total <= 1000:
        while len(ids) < total:
            pagina = cliente.get(caminho, {"status": "active", "limit": 50, "offset": len(ids)}) or {}
            resultados = pagina.get("results") or []
            if not resultados:
                break
            ids.extend(resultados)
            time.sleep(PAUSA_ENTRE_CHAMADAS)
    else:
        # Acima de 1000 anúncios o Mercado Livre exige o modo "scan".
        ids = []
        params = {"status": "active", "search_type": "scan", "limit": 100}
        while True:
            pagina = cliente.get(caminho, params) or {}
            resultados = pagina.get("results") or []
            if not resultados:
                break
            ids.extend(resultados)
            scroll = pagina.get("scroll_id")
            if not scroll:
                break
            params = {"status": "active", "search_type": "scan", "limit": 100, "scroll_id": scroll}
            time.sleep(PAUSA_ENTRE_CHAMADAS)

    return list(dict.fromkeys(ids))  # tira repetidos, mantendo a ordem


def buscar_detalhes(cliente, ids):
    detalhes = {}
    for i in range(0, len(ids), 20):  # o Mercado Livre aceita até 20 por chamada
        lote = ids[i:i + 20]
        resposta = cliente.get("/items", {"ids": ",".join(lote), "attributes": CAMPOS_DOS_ANUNCIOS}) or []
        for item in resposta:
            corpo = item.get("body") or {}
            if item.get("code") == 200 and corpo.get("id"):
                detalhes[corpo["id"]] = corpo
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    return detalhes


def buscar_categorias(cliente, detalhes):
    """Limite do título e campos da ficha técnica de cada categoria (uma consulta por categoria)."""
    categorias = {}
    ultimo_erro = None
    for categoria in dict.fromkeys(d.get("category_id") for d in detalhes.values() if d.get("category_id")):
        dados = {"max_titulo": None, "atributos": None}
        try:
            info = cliente.get(f"/categories/{categoria}")
            ajustes = info.get("settings") if isinstance(info, dict) else None
            if isinstance(ajustes, dict):
                dados["max_titulo"] = ajustes.get("max_title_length")
            atributos = cliente.get(f"/categories/{categoria}/attributes")
            dados["atributos"] = atributos if isinstance(atributos, list) else None
        except ml_api.ErroLogin:
            raise
        except ml_api.ErroML as e:
            ultimo_erro = e
        categorias[categoria] = dados
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    sem_ficha = sum(1 for c in categorias.values() if c["atributos"] is None)
    if sem_ficha:
        print(f"  Não consegui ler a ficha técnica de {sem_ficha} categoria(s). Último erro: {ultimo_erro}")
    return categorias


def _andamento(progresso, n, total):
    """Mostra o andamento no Prompt de Comando, ou avisa quem pediu (o site mostra numa página)."""
    if progresso:
        progresso(n, total)
    elif n % 10 == 0 or n == total:
        print(f"  {n}/{total}", end="\r", flush=True)


def buscar_visitas(cliente, ids, dias, progresso=None):
    visitas = {}
    ultimo_erro = None
    for n, item_id in enumerate(ids, 1):
        try:
            r = cliente.get(f"/items/{item_id}/visits/time_window", {"last": dias, "unit": "day"}) or {}
            visitas[item_id] = int(r.get("total_visits") or 0)
        except ml_api.ErroLogin:
            raise
        except ml_api.ErroML as e:
            visitas[item_id] = None
            ultimo_erro = e
        _andamento(progresso, n, len(ids))
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    if progresso is None:
        print()
    sem_visitas = sum(1 for v in visitas.values() if v is None)
    if sem_visitas:
        print(f"  Não consegui ler as visitas de {sem_visitas} anúncio(s). Último erro: {ultimo_erro}")
    return visitas


def buscar_vendas(cliente, user_id, dias):
    """Soma as unidades vendidas por anúncio nos pedidos pagos do período."""
    agora = datetime.now(timezone.utc)
    inicio = agora - timedelta(days=dias)
    formato = "%Y-%m-%dT%H:%M:%S.000-00:00"
    params = {
        "seller": user_id,
        "order.status": "paid",
        "order.date_created.from": inicio.strftime(formato),
        "order.date_created.to": agora.strftime(formato),
        "sort": "date_desc",
        "limit": 50,
        "offset": 0,
    }
    vendas = {}
    while True:
        pagina = cliente.get("/orders/search", params) or {}
        resultados = pagina.get("results") or []
        for pedido in resultados:
            for linha in pedido.get("order_items") or []:
                item_id = (linha.get("item") or {}).get("id")
                if item_id:
                    vendas[item_id] = vendas.get(item_id, 0) + int(linha.get("quantity") or 0)
        total = (pagina.get("paging") or {}).get("total", 0)
        params["offset"] += len(resultados)
        if not resultados or params["offset"] >= total:
            break
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    return vendas


def buscar_qualidade(cliente, ids, progresso=None):
    """Nota de qualidade que o Mercado Livre dá a cada anúncio e o que ele pede para melhorar.

    Ela é um extra: se não der para ler, o relatório sai do mesmo jeito, sem a nota.
    """
    qualidade = {}
    ultimo_erro = None
    sem_calculo = None  # o que o Mercado Livre responde quando ainda não calculou a nota
    for n, item_id in enumerate(ids, 1):
        try:
            qualidade[item_id] = analise.ler_qualidade(cliente.get(f"/item/{item_id}/performance"))
        except ml_api.ErroML as e:
            if e.status == 404:
                qualidade[item_id] = analise.ler_qualidade(None)
                sem_calculo = e
            else:
                ultimo_erro = e
                # Sem permissão e login recusado valem para todos os anúncios. Se os 3 primeiros falharam,
                # o problema também não é de um anúncio só. Nesses casos, não adianta continuar perguntando.
                if isinstance(e, ml_api.ErroLogin) or e.status == 403 or (not qualidade and n >= 3):
                    break
        _andamento(progresso, n, len(ids))
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    if progresso is None:
        print()
    sem_nota = len(ids) - len(qualidade)
    if sem_nota:
        print(f"  Não consegui ler a nota de qualidade de {sem_nota} anúncio(s). Último erro: {ultimo_erro}")
    elif sem_calculo and all(q["nota"] is None and not q["nivel"] for q in qualidade.values()):
        print(f"  O Mercado Livre ainda não tem nota para nenhum dos anúncios (resposta: {sem_calculo}).")
    return qualidade


# ---------------------------------------------------------------- análise

def montar_linhas(ids, detalhes, visitas, vendas, categorias=None, qualidade=None):
    categorias = categorias or {}
    qualidade = qualidade or {}
    linhas = []
    for item_id in ids:
        d = detalhes.get(item_id, {})
        v = visitas.get(item_id)
        s = None if vendas is None else vendas.get(item_id, 0)
        conversao = (s / v) if (v and s is not None) else None
        situacao = analise.classificar(v, s)
        nota = qualidade.get(item_id)
        categoria = categorias.get(d.get("category_id"))
        sugestoes = analise.sugerir(d, situacao, categoria, nota)
        ficha = analise.contar_ficha(d, (categoria or {}).get("atributos"))
        fotos = d.get("pictures")
        linhas.append({
            "id": item_id,
            "titulo": d.get("title") or "",
            "preco": d.get("price"),
            "estoque": d.get("available_quantity"),
            "visitas": v,
            "vendas": s,
            "conversao": conversao,
            "situacao": situacao,
            "o_que_olhar": analise.SITUACOES[situacao],
            "sugestoes": sugestoes,
            "pontos": analise.pontos(sugestoes),
            "qualidade": analise.texto_qualidade(nota),
            "fotos": len(fotos) if isinstance(fotos, list) else None,
            "ficha": f"{ficha[0]} de {ficha[1]} campos" if ficha else "?",
            "link": d.get("permalink") or "",
        })
    # Primeiro a situação; dentro dela, quem tem mais coisas importantes para mudar e depois mais visitas.
    linhas.sort(key=lambda l: (analise.ORDEM.index(l["situacao"]), -l["pontos"], -(l["visitas"] or 0)))
    return linhas


# ---------------------------------------------------------------- saída

def _num_br(valor, casas=2):
    if valor is None:
        return ""
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _texto(valor):
    return "?" if valor is None else str(valor)


def _o_que_mudar(sugestoes):
    if not sugestoes:
        return "Nenhuma mudança sugerida"
    return " | ".join(f"{n}) {s['texto']}" for n, s in enumerate(sugestoes, 1))


def montar_csv(linhas, dias):
    """O CSV do relatório como texto. O PC salva num arquivo; o site entrega direto ao navegador."""
    cabecalho = ["id", "titulo", "preco", "estoque", f"visitas_{dias}d", f"vendas_{dias}d",
                 "conversao_%", "situacao", "o_que_olhar", "o_que_mudar", "qualidade_ml", "fotos",
                 "ficha_tecnica", "link"]
    f = io.StringIO(newline="")
    escritor = csv.writer(f, delimiter=";")  # ";" é o separador do Excel em português
    escritor.writerow(cabecalho)
    for l in linhas:
        escritor.writerow([
            l["id"], l["titulo"], _num_br(l["preco"]), _texto(l["estoque"]),
            _texto(l["visitas"]), _texto(l["vendas"]),
            _num_br(l["conversao"] * 100 if l["conversao"] is not None else None, 1),
            l["situacao"], l["o_que_olhar"], _o_que_mudar(l["sugestoes"]), l["qualidade"],
            _texto(l["fotos"]), l["ficha"], l["link"],
        ])
    return f.getvalue()


def salvar_csv(linhas, dias):
    texto = montar_csv(linhas, dias).encode("utf-8-sig")  # o BOM faz o Excel ler os acentos certos
    destino = ARQ_RELATORIO
    try:
        f = open(destino, "wb")
    except PermissionError:
        # O arquivo anterior provavelmente está aberto no Excel.
        destino = destino.with_name(f"relatorio_anuncios_{datetime.now():%Y%m%d_%H%M%S}.csv")
        f = open(destino, "wb")
    with f:
        f.write(texto)
    return destino


def _encurtar(titulo):
    return (titulo[:45] + "...") if len(titulo) > 48 else titulo


def mostrar_resumo(linhas, dias):
    print(f"\n=== Resumo dos últimos {dias} dias ===")
    for situacao in analise.ORDEM:
        qtd = sum(1 for l in linhas if l["situacao"] == situacao)
        if qtd:
            print(f"  {situacao:<24} {qtd:>4}")

    com_problema = analise.PROBLEMA_DE_VENDA | analise.PROBLEMA_DE_VISITA
    prioridade = [l for l in linhas if l["sugestoes"] or l["situacao"] in com_problema][:10]
    if prioridade:
        print("\nComece por estes (o que mudar em cada um):")
        for n, l in enumerate(prioridade, 1):
            print(f"  {n:>2}. {_encurtar(l['titulo']):<48} {_texto(l['visitas']):>6} visitas  "
                  f"{_texto(l['vendas']):>4} vendas")
            print(f"      Nota do ML: {l['qualidade']}  |  Fotos: {_texto(l['fotos'])}  |  "
                  f"Ficha técnica: {l['ficha']}")
            textos = [s["texto"] for s in l["sugestoes"]] or [l["o_que_olhar"]]
            for texto in textos[:SUGESTOES_NA_TELA]:
                print(textwrap.fill(texto, width=100, initial_indent="      - ", subsequent_indent="        "))
            if len(textos) > SUGESTOES_NA_TELA:
                print(f"        (mais {len(textos) - SUGESTOES_NA_TELA} no CSV)")

    melhores = sorted((l for l in linhas if l["vendas"]), key=lambda l: -l["vendas"])[:5]
    if melhores:
        print("\nOs que mais vendem:")
        for n, l in enumerate(melhores, 1):
            print(f"  {n:>2}. {_encurtar(l['titulo']):<48} {l['vendas']:>4} vendas")


# ---------------------------------------------------------------- principal

def coletar(cliente, user_id, dias, limite=None, etapa=None, progresso=None):
    """Busca tudo que o relatório precisa, na ordem. Devolve um dicionário com os argumentos de montar_linhas.

    etapa(texto) recebe o nome de cada etapa; progresso(feitos, total) recebe o andamento das chamadas
    por anúncio. O PC mostra os dois no Prompt de Comando; o site mostra numa página de andamento.
    limite corta a lista de anúncios (o site lê só uma quantidade fixa por relatório).
    """
    def dizer(texto):
        if etapa:
            etapa(texto)

    dizer("Buscando anúncios ativos...")
    ids = listar_ids_ativos(cliente, user_id)
    if limite:
        ids = ids[:limite]
    if not ids:
        return {"ids": []}
    achados = "1 anúncio encontrado" if len(ids) == 1 else f"{len(ids)} anúncios encontrados"
    dizer(f"{achados}. Buscando detalhes...")
    detalhes = buscar_detalhes(cliente, ids)

    dizer("Buscando a ficha técnica de cada categoria...")
    categorias = buscar_categorias(cliente, detalhes)

    dizer("Buscando visitas (uma consulta por anúncio, pode levar um tempinho)...")
    visitas = buscar_visitas(cliente, ids, dias, progresso)

    dizer("Buscando vendas...")
    try:
        vendas = buscar_vendas(cliente, user_id, dias)
    except ml_api.ErroLogin:
        raise
    except ml_api.ErroML as e:
        print(f"  Não consegui ler as vendas ({e}). Elas vão aparecer como '?'.")
        vendas = None

    dizer("Buscando a nota de qualidade do Mercado Livre (uma consulta por anúncio)...")
    qualidade = buscar_qualidade(cliente, ids, progresso)
    return {"ids": ids, "detalhes": detalhes, "categorias": categorias,
            "visitas": visitas, "vendas": vendas, "qualidade": qualidade}


def main():
    parser = argparse.ArgumentParser(description="Relatório dos seus anúncios ativos no Mercado Livre")
    parser.add_argument("--dias", type=int, default=30, help="período em dias, de 1 a 150 (padrão: 30)")
    dias = max(1, min(parser.parse_args().dias, 150))

    try:
        cliente = ml_api.MercadoLivre()
        eu = cliente.obter_usuario()
        print(f"Conta: {eu.get('nickname')}  |  período: últimos {dias} dias")
        dados = coletar(cliente, eu["id"], dias, etapa=print)
    except ml_api.ErroML as e:
        print("\nNão deu certo:", e)
        sys.exit(1)

    if not dados["ids"]:
        print("Nenhum anúncio ativo nessa conta.")
        return

    linhas = montar_linhas(**dados)
    mostrar_resumo(linhas, dias)
    destino = salvar_csv(linhas, dias)
    print(f"\nRelatório completo salvo em: {destino}")
    print("Obs.: as visitas podem levar até 48 horas para aparecer no Mercado Livre.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado.")
        sys.exit(1)
