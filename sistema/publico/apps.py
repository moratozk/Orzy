from django.apps import AppConfig


class PublicoConfig(AppConfig):
    """Páginas abertas a todos: início, textos legais, erros, robots.txt e saúde. Guarda também os arquivos de
    /static/ e o modelo base das páginas."""

    name = "publico"
