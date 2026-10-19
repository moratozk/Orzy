"""Entrada do servidor (gunicorn orzy.wsgi, ou o runserver do Django para testar no computador).

Liga também, em segundo plano, as limpezas que a Política de Privacidade promete: as sessões vencidas a cada minuto e
o histórico com mais de 12 meses uma vez por dia, mesmo sem ninguém usando o site.
"""

import os
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orzy.settings")

application = get_wsgi_application()

from relatorios import limpezas  # noqa: E402 (precisa do Django já configurado)

limpezas.ligar(threading.Event())
