"""Liga o site: python -m web.servidor (com as variáveis de ambiente do site configuradas). Ver web/LEIA-ME.md."""

import logging
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from . import configuracao
from .app import Site

LIMITE_CORPO = 10_000  # bytes: formulário pequeno, nada mais que isso é necessário
DIAS_DE_HISTORICO = 365  # relatórios mais antigos são apagados ao ligar o servidor


class Manipulador(BaseHTTPRequestHandler):
    site = None  # preenchido em main()
    server_version = "Orzy"
    sys_version = ""

    def do_GET(self):
        self._responder("GET")

    def do_POST(self):
        self._responder("POST")

    def _responder(self, metodo):
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
        self.wfile.write(dados)

    def log_message(self, formato, *args):
        # Só o caminho, sem a busca: o ?code=... do Mercado Livre não pode ir para o registro do servidor.
        logging.info("%s %s", self.command, urlsplit(self.path).path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        config = configuracao.carregar()
    except configuracao.ErroConfiguracao as e:
        print(f"Não dá para ligar o site: {e}.", file=sys.stderr)
        sys.exit(1)

    site = Site(config)
    apagados = site.historico.apagar_antigos(DIAS_DE_HISTORICO)
    if apagados:
        logging.info("Histórico: %d relatório(s) com mais de %d dias foram apagados.", apagados, DIAS_DE_HISTORICO)

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
