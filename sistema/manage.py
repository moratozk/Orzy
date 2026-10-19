"""Comandos do Django para o sistema do Orzy (ver sistema/LEIA-ME.md). Rodar de dentro da pasta sistema/."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orzy.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
