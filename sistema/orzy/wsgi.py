"""Entrada do servidor (gunicorn orzy.wsgi, ou o runserver do Django para testar no computador).

Liga também, em segundo plano, as limpezas que a Política de Privacidade promete, mesmo sem ninguém usando o site: as
sessões vencidas a cada minuto e, uma vez por dia, o histórico com mais de 12 meses e a conferência das contas
(relatorios/limpezas.py).
"""

import os
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orzy.settings")

application = get_wsgi_application()

from relatorios import limpezas  # noqa: E402 (precisa do Django já configurado)

limpezas.ligar(threading.Event())
