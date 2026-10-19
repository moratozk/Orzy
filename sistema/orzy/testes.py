"""Executor dos testes do sistema: junta os arquivos de /static/ antes (as páginas usam os nomes com o resumo do
conteúdo, que o collectstatic cria), para `python manage.py test` funcionar sem um passo a mais."""

import logging

from django.core.management import call_command
from django.test.runner import DiscoverRunner


class Executor(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        call_command("collectstatic", interactive=False, verbosity=0)
        # Os testes pedem páginas que não existem e pedidos recusados de propósito: sem uma linha para cada um.
        for nome, nivel in (("django.request", logging.ERROR), ("django.security.csrf", logging.ERROR),
                            ("django.security.DisallowedHost", logging.CRITICAL)):
            logging.getLogger(nome).setLevel(nivel)
