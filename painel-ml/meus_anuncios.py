"""
Passo 2: lista seus anúncios ativos com visitas, vendas e conversão do período,
e diz o que olhar em cada um.

Como usar (no Prompt de Comando, dentro desta pasta):
    python meus_anuncios.py             últimos 30 dias
    python meus_anuncios.py --dias 60   outro período (1 a 150 dias)

Gera o arquivo relatorio_anuncios.csv, que abre direto no Excel.
"""

import argparse
import csv
import sys
import time
from datetime import datetime, timedelta, timezone

import ml_api

# Pontos de partida para a classificação. Ajuste à vontade: não são regras do Mercado Livre.
POUCAS_VISITAS = 30      # abaixo disso no período, o anúncio quase não está sendo encontrado
CONVERSAO_BAIXA = 0.01   # 1%: abaixo disso, vende pouco para as visitas que recebe
PAUSA_ENTRE_CHAMADAS = 0.05

# Em ordem de prioridade: os primeiros são os que mais valem a pena mexer.
SITUACOES = {
    "VISITA SEM VENDA": "As pessoas veem e não compram: revise preço, fotos, frete e descrição.",
    "CONVERTE POUCO": "Vende pouco para as visitas que tem: compare preço e frete com os concorrentes.",
    "POUCA VISITA": "Quase ninguém encontra: revise título, palavras-chave, categoria e ficha técnica.",
    "VENDE, MAS POUCO VISTO": "Quem vê, compra: vale melhorar o título ou anunciar para ganhar visitas.",
    "VENDENDO BEM": "Está funcionando: use como modelo para os outros anúncios.",
    "SEM DADOS": "Não consegui ler as visitas ou as vendas deste anúncio.",
}
ORDEM = list(SITUACOES)

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
    campos = "id,title,price,currency_id,available_quantity,status,permalink"
    detalhes = {}
    for i in range(0, len(ids), 20):  # o Mercado Livre aceita até 20 por chamada
        lote = ids[i:i + 20]
        resposta = cliente.get("/items", {"ids": ",".join(lote), "attributes": campos}) or []
        for item in resposta:
            corpo = item.get("body") or {}
            if item.get("code") == 200 and corpo.get("id"):
                detalhes[corpo["id"]] = corpo
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    return detalhes


def buscar_visitas(cliente, ids, dias):
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
        if n % 10 == 0 or n == len(ids):
            print(f"  {n}/{len(ids)}", end="\r", flush=True)
        time.sleep(PAUSA_ENTRE_CHAMADAS)
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


# ---------------------------------------------------------------- análise

def classificar(visitas, vendas):
    if visitas is None or vendas is None:
        return "SEM DADOS"
    if visitas < POUCAS_VISITAS:
        return "VENDE, MAS POUCO VISTO" if vendas > 0 else "POUCA VISITA"
    if vendas == 0:
        return "VISITA SEM VENDA"
    if vendas / visitas < CONVERSAO_BAIXA:
        return "CONVERTE POUCO"
    return "VENDENDO BEM"


def montar_linhas(ids, detalhes, visitas, vendas):
    linhas = []
    for item_id in ids:
        d = detalhes.get(item_id, {})
        v = visitas.get(item_id)
        s = None if vendas is None else vendas.get(item_id, 0)
        conversao = (s / v) if (v and s is not None) else None
        situacao = classificar(v, s)
        linhas.append({
            "id": item_id,
            "titulo": d.get("title") or "",
            "preco": d.get("price"),
            "estoque": d.get("available_quantity"),
            "visitas": v,
            "vendas": s,
            "conversao": conversao,
            "situacao": situacao,
            "o_que_olhar": SITUACOES[situacao],
            "link": d.get("permalink") or "",
        })
    linhas.sort(key=lambda l: (ORDEM.index(l["situacao"]), -(l["visitas"] or 0)))
    return linhas


# ---------------------------------------------------------------- saída

def _num_br(valor, casas=2):
    if valor is None:
        return ""
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _texto(valor):
    return "?" if valor is None else str(valor)


def salvar_csv(linhas, dias):
    cabecalho = ["id", "titulo", "preco", "estoque", f"visitas_{dias}d", f"vendas_{dias}d",
                 "conversao_%", "situacao", "o_que_olhar", "link"]
    destino = ARQ_RELATORIO
    try:
        f = open(destino, "w", encoding="utf-8-sig", newline="")
    except PermissionError:
        # O arquivo anterior provavelmente está aberto no Excel.
        destino = destino.with_name(f"relatorio_anuncios_{datetime.now():%Y%m%d_%H%M%S}.csv")
        f = open(destino, "w", encoding="utf-8-sig", newline="")
    with f:
        escritor = csv.writer(f, delimiter=";")  # ";" é o separador do Excel em português
        escritor.writerow(cabecalho)
        for l in linhas:
            escritor.writerow([
                l["id"], l["titulo"], _num_br(l["preco"]), _texto(l["estoque"]),
                _texto(l["visitas"]), _texto(l["vendas"]),
                _num_br(l["conversao"] * 100 if l["conversao"] is not None else None, 1),
                l["situacao"], l["o_que_olhar"], l["link"],
            ])
    return destino


def mostrar_resumo(linhas, dias):
    print(f"\n=== Resumo dos últimos {dias} dias ===")
    for situacao in ORDEM:
        qtd = sum(1 for l in linhas if l["situacao"] == situacao)
        if qtd:
            print(f"  {situacao:<24} {qtd:>4}")

    prioridade = [l for l in linhas if l["situacao"] in ("VISITA SEM VENDA", "CONVERTE POUCO")][:10]
    if prioridade:
        print("\nComece por estes (mais visitas e pouca ou nenhuma venda):")
        for n, l in enumerate(prioridade, 1):
            titulo = (l["titulo"][:45] + "...") if len(l["titulo"]) > 48 else l["titulo"]
            print(f"  {n:>2}. {titulo:<48} {_texto(l['visitas']):>6} visitas  {_texto(l['vendas']):>4} vendas")

    melhores = sorted((l for l in linhas if l["vendas"]), key=lambda l: -l["vendas"])[:5]
    if melhores:
        print("\nOs que mais vendem:")
        for n, l in enumerate(melhores, 1):
            titulo = (l["titulo"][:45] + "...") if len(l["titulo"]) > 48 else l["titulo"]
            print(f"  {n:>2}. {titulo:<48} {l['vendas']:>4} vendas")


# ---------------------------------------------------------------- principal

def main():
    parser = argparse.ArgumentParser(description="Relatório dos seus anúncios ativos no Mercado Livre")
    parser.add_argument("--dias", type=int, default=30, help="período em dias, de 1 a 150 (padrão: 30)")
    dias = max(1, min(parser.parse_args().dias, 150))

    try:
        cliente = ml_api.MercadoLivre()
        eu = cliente.obter_usuario()
        user_id = eu["id"]
        print(f"Conta: {eu.get('nickname')}  |  período: últimos {dias} dias")

        print("Buscando anúncios ativos...")
        ids = listar_ids_ativos(cliente, user_id)
        if not ids:
            print("Nenhum anúncio ativo nessa conta.")
            return
        print(f"  {len(ids)} anúncios encontrados. Buscando detalhes...")
        detalhes = buscar_detalhes(cliente, ids)

        print("Buscando visitas (uma consulta por anúncio, pode levar um tempinho)...")
        visitas = buscar_visitas(cliente, ids, dias)

        print("Buscando vendas...")
        try:
            vendas = buscar_vendas(cliente, user_id, dias)
        except ml_api.ErroLogin:
            raise
        except ml_api.ErroML as e:
            print(f"  Não consegui ler as vendas ({e}). Elas vão aparecer como '?'.")
            vendas = None

    except ml_api.ErroML as e:
        print("\nNão deu certo:", e)
        sys.exit(1)

    linhas = montar_linhas(ids, detalhes, visitas, vendas)
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
