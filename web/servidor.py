"""Liga o site: python -m web.servidor (com as variáveis de ambiente do site configuradas). Ver web/LEIA-ME.md."""

import logging
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from . import configuracao
from .app import Site
from .historico import DIAS_DE_HISTORICO

LIMITE_CORPO = 10_000  # bytes: formulário pequeno, nada mais que isso é necessário
UM_DIA = 24 * 3600
UM_MINUTO = 60


class Manipulador(BaseHTTPRequestHandler):
    site = None  # preenchido em main()
    server_version = "Orzy"
    sys_version = ""
    timeout = 60  # segundos: uma conexão parada é fechada e não prende uma thread do servidor

    def do_GET(self):
        self._responder("GET")

    def do_POST(self):
        self._responder("POST")

    def do_HEAD(self):
        # Verificadores de link e monitores usam HEAD: mesma resposta do GET, sem o corpo.
        self._responder("GET", com_corpo=False)

    def _responder(self, metodo, com_corpo=True):
        try:
            tamanho = max(0, int(self.headers.get("Content-Length") or 0))
        except ValueError:
            tamanho = 0
        corpo = self.rfile.read(min(tamanho, LIMITE_CORPO)) if tamanho else b""
        status, cabecalhos, dados = self.site.tratar(metodo, self.path, self.headers, corpo)
        self.send_response(status)
        for nome, valor in cabecalhos:
            self.send_header(nome, valor)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        if com_corpo:
            self.wfile.write(dados)

    def log_message(self, formato, *args):
        # Só o caminho, sem a busca: o ?code=... do Mercado Livre não pode ir para o registro do servidor.
        # Num erro antes de ler o pedido (uma conexão parada, por exemplo), ainda não há comando nem caminho.
        caminho = urlsplit(getattr(self, "path", "") or "").path
        logging.info("%s %s", getattr(self, "command", None) or "-", caminho or "-")


def apagar_antigos_todo_dia(historico, parar, intervalo=UM_DIA):
    """Apaga os relatórios e as contagens do beta com mais de 12 meses agora e depois a cada intervalo, até `parar`.

    A Política de Privacidade promete 12 meses: com o servidor ligado por semanas, não basta apagar ao ligar.
    """
    while True:
        try:
            apagados = historico.apagar_antigos(DIAS_DE_HISTORICO)
            if apagados:
                logging.info("Histórico: %d relatório(s) com mais de %d dias foram apagados.",
                             apagados, DIAS_DE_HISTORICO)
        except Exception:
            logging.exception("Não consegui apagar o histórico antigo; tento de novo no próximo ciclo")
        if parar.wait(intervalo):
            return


def apagar_sessoes_vencidas_sempre(sessoes, parar, intervalo=UM_MINUTO):
    """Apaga as sessões vencidas a cada intervalo, até `parar`, mesmo sem ninguém usando o site.

    A Política de Privacidade promete tirar o login da memória no máximo 8 horas depois da entrada: sem isto, uma
    sessão vencida só sai no próximo pedido. Apaga um intervalo antes do prazo, para nenhuma passar dele.
    """
    while True:
        try:
            sessoes.limpar(antecedencia=intervalo)
        except Exception:
            logging.exception("Não consegui apagar as sessões vencidas; tento de novo no próximo ciclo")
        if parar.wait(intervalo):
            return


def ligar_limpezas(site, parar):
    """Liga em segundo plano a limpeza do histórico (uma vez por dia) e a das sessões (a cada minuto)."""
    for alvo, guardados, nome in ((apagar_antigos_todo_dia, site.historico, "limpeza-do-historico"),
                                  (apagar_sessoes_vencidas_sempre, site.sessoes, "limpeza-das-sessoes")):
        threading.Thread(target=alvo, args=(guardados, parar), name=nome, daemon=True).start()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        config = configuracao.carregar()
    except configuracao.ErroConfiguracao as e:
        print(f"Não dá para ligar o site: {e}.", file=sys.stderr)
        sys.exit(1)

    site = Site(config)
    ligar_limpezas(site, threading.Event())

    manipulador = type("ManipuladorOrzy", (Manipulador,), {"site": site})
    servidor = ThreadingHTTPServer((config.host, config.porta), manipulador)
    logging.info("Orzy no ar em %s (porta %s).", config.url_base, config.porta)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        logging.info("Desligando.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
