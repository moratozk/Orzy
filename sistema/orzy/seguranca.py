"""Cabeçalhos que o Django não põe sozinho, e os filtros do registro do servidor."""

import logging
import re


class SemGuardarNoNavegador:
    """As páginas do Orzy não ficam guardadas no navegador nem no caminho (Cache-Control: no-store), a não ser que a
    resposta já diga outra coisa, como o robots.txt. Os arquivos de /static/ não passam por aqui: o WhiteNoise
    responde antes, com o prazo longo de quem tem o resumo do conteúdo no nome."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resposta = self.get_response(request)
        resposta.headers.setdefault("Cache-Control", "no-store")
        return resposta


class UmaLinhaSo(logging.Filter):
    """Tira o rastro do erro da linha: um pedido com outro endereço (Host), coisa de robô que varre a internet, deixa
    só a mensagem do Django, que diz o endereço recusado."""

    def filter(self, registro):
        registro.exc_info = registro.exc_text = None
        return True


class SemBuscaNoRegistro(logging.Filter):
    """Tira a busca do endereço ("?code=...") da linha que o runserver escreve para cada pedido: o código do Mercado
    Livre não fica no registro, nem no computador de quem testa."""

    def filter(self, registro):
        if registro.args and isinstance(registro.args, tuple) and isinstance(registro.args[0], str):
            registro.args = (re.sub(r"\?\S*", "", registro.args[0], count=1),) + registro.args[1:]
        return True
