"""Testes do sistema (Django) contra o Mercado Livre simulado (testes/ml_simulado.py, na pasta principal do Orzy).

Rodar de dentro da pasta sistema/, com o PostgreSQL ligado e as variáveis de ambiente do LEIA-ME:
    python manage.py test testes

O Django cria um banco só para os testes (test_ mais o nome do banco) e apaga no fim. Nada aqui fala com o Mercado
Livre de verdade.
"""

import sys
from pathlib import Path

# O Mercado Livre simulado é o mesmo dos testes do programa do PC.
PASTA_SIMULADO = str(Path(__file__).resolve().parent.parent.parent / "testes")
if PASTA_SIMULADO not in sys.path:
    sys.path.insert(0, PASTA_SIMULADO)
