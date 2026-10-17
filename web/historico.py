"""Histórico dos relatórios, num arquivo SQLite no servidor.

Guarda só o que o relatório mostra: número e título dos anúncios e os números deles.
Nada de token e nenhum dado de comprador. Guarda também as contagens do beta (ver contagens.py): só números por
dia, sem dizer de qual conta.
"""

import contextlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone

import analise

from . import contagens

DIAS_DE_HISTORICO = 365  # relatórios mais antigos são apagados ao ligar o servidor e depois uma vez por dia

ESQUEMA = """
CREATE TABLE IF NOT EXISTS relatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ml_user_id INTEGER NOT NULL,
    criado_em TEXT NOT NULL,
    dias INTEGER NOT NULL,
    total INTEGER NOT NULL,
    resumo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS anuncios (
    relatorio_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    titulo TEXT NOT NULL,
    visitas INTEGER,
    vendas INTEGER,
    situacao TEXT NOT NULL,
    pontos INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS anuncios_do_relatorio ON anuncios (relatorio_id);
CREATE TABLE IF NOT EXISTS contagens (
    dia TEXT NOT NULL,
    nome TEXT NOT NULL,
    valor INTEGER NOT NULL,
    PRIMARY KEY (dia, nome)
);
"""

COLUNAS_ANUNCIO = ("id", "titulo", "visitas", "vendas", "situacao", "pontos")


def _agora():
    return datetime.now(timezone.utc)


class Historico:
    def __init__(self, caminho, agora=_agora):
        self.caminho = caminho
        self._agora = agora
        with self._conectar() as con:
            con.executescript(ESQUEMA)

    @contextlib.contextmanager
    def _conectar(self):
        con = sqlite3.connect(self.caminho)
        try:
            with con:  # confirma ao sair do bloco; se der erro, desfaz
                yield con
        finally:
            con.close()

    def salvar(self, ml_user_id, dias, linhas):
        resumo = {situacao: sum(1 for l in linhas if l["situacao"] == situacao) for situacao in analise.ORDEM}
        with self._conectar() as con:
            cursor = con.execute(
                "INSERT INTO relatorios (ml_user_id, criado_em, dias, total, resumo) VALUES (?, ?, ?, ?, ?)",
                (int(ml_user_id), self._agora().isoformat(timespec="seconds"), dias, len(linhas),
                 json.dumps(resumo)))
            id_ = cursor.lastrowid
            con.executemany(
                "INSERT INTO anuncios (relatorio_id, item_id, titulo, visitas, vendas, situacao, pontos) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(id_, l["id"], l["titulo"], l["visitas"], l["vendas"], l["situacao"], l["pontos"])
                 for l in linhas])
        return id_

    def listar(self, ml_user_id):
        with self._conectar() as con:
            linhas = con.execute(
                "SELECT id, criado_em, dias, total, resumo FROM relatorios "
                "WHERE ml_user_id = ? ORDER BY id DESC LIMIT 100", (int(ml_user_id),)).fetchall()
        return [{"id": i, "criado_em": c, "dias": d, "total": t, "resumo": json.loads(r)}
                for i, c, d, t, r in linhas]

    def ver(self, ml_user_id, relatorio_id):
        """Um relatório salvo, só se for da conta pedida. Devolve None se não for."""
        with self._conectar() as con:
            cabecalho = con.execute(
                "SELECT id, criado_em, dias, total, resumo FROM relatorios WHERE id = ? AND ml_user_id = ?",
                (int(relatorio_id), int(ml_user_id))).fetchone()
            if cabecalho is None:
                return None
            anuncios = con.execute(
                "SELECT item_id, titulo, visitas, vendas, situacao, pontos FROM anuncios "
                "WHERE relatorio_id = ? ORDER BY rowid", (cabecalho[0],)).fetchall()
        id_, criado, dias, total, resumo = cabecalho
        return {"id": id_, "criado_em": criado, "dias": dias, "total": total, "resumo": json.loads(resumo),
                "anuncios": [dict(zip(COLUNAS_ANUNCIO, a)) for a in anuncios]}

    def id_do_anterior(self, ml_user_id, relatorio_id):
        """O relatório guardado logo antes deste, da mesma conta e do mesmo período: é com ele que se compara.

        Devolve o número dele, ou None se não houver (ou se o relatório pedido não for da conta).
        """
        with self._conectar() as con:
            linha = con.execute(
                "SELECT antes.id FROM relatorios AS este JOIN relatorios AS antes "
                "ON antes.ml_user_id = este.ml_user_id AND antes.dias = este.dias AND antes.id < este.id "
                "WHERE este.id = ? AND este.ml_user_id = ? ORDER BY antes.id DESC LIMIT 1",
                (int(relatorio_id), int(ml_user_id))).fetchone()
        return linha[0] if linha else None

    def apagar(self, ml_user_id):
        """Apaga todos os relatórios da conta. Devolve quantos foram apagados."""
        with self._conectar() as con:
            con.execute("DELETE FROM anuncios WHERE relatorio_id IN "
                        "(SELECT id FROM relatorios WHERE ml_user_id = ?)", (int(ml_user_id),))
            return con.execute("DELETE FROM relatorios WHERE ml_user_id = ?", (int(ml_user_id),)).rowcount

    def apagar_antigos(self, dias):
        """Apaga os relatórios e os dias de contagem do beta com mais de `dias` dias. Devolve quantos relatórios."""
        limite = self._agora() - timedelta(days=dias)
        antes = limite.isoformat(timespec="seconds")
        with self._conectar() as con:
            con.execute("DELETE FROM anuncios WHERE relatorio_id IN "
                        "(SELECT id FROM relatorios WHERE criado_em < ?)", (antes,))
            apagados = con.execute("DELETE FROM relatorios WHERE criado_em < ?", (antes,)).rowcount
            # Dia de Brasília. Sai também o dia em que o limite cai: ele já tem contagens mais velhas que o limite.
            con.execute("DELETE FROM contagens WHERE dia <= ?", (contagens.hoje(limite),))
        return apagados

    # ------------------------------------------------------------ contagens do beta (ver contagens.py)

    def somar_contagens(self, dia, valores):
        """Soma às contagens do dia ({"logins": 1}, por exemplo). Só números: nada de conta."""
        with self._conectar() as con:
            con.executemany(
                "INSERT INTO contagens (dia, nome, valor) VALUES (?, ?, ?) "
                "ON CONFLICT (dia, nome) DO UPDATE SET valor = valor + excluded.valor",
                [(dia, nome, int(valor)) for nome, valor in valores.items()])

    def ler_contagens(self):
        """{dia: {nome: valor}} de todos os dias que têm alguma contagem."""
        dias = {}
        with self._conectar() as con:
            for dia, nome, valor in con.execute("SELECT dia, nome, valor FROM contagens"):
                dias.setdefault(dia, {})[nome] = valor
        return dias

    def ultimo_total_de_cada_conta(self):
        """Quantos anúncios tem o último relatório guardado de cada conta, do menor para o maior, sem dizer a conta."""
        with self._conectar() as con:
            linhas = con.execute("SELECT total FROM relatorios WHERE id IN "
                                 "(SELECT MAX(id) FROM relatorios GROUP BY ml_user_id)").fetchall()
        return sorted(total for total, in linhas)
