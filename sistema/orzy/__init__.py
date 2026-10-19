"""Sistema do Orzy em Django (fase 4). Ver sistema/LEIA-ME.md e docs/02-roadmap.md.

O programa do PC (painel-ml/) não é um pacote Python. Este arquivo põe a pasta dele no caminho de busca, para o sistema
usar as mesmas regras (analise.py) e a mesma coleta (meus_anuncios.py) sem copiar código.
"""

import sys
from pathlib import Path

PASTA_PAINEL = str(Path(__file__).resolve().parent.parent.parent / "painel-ml")
if PASTA_PAINEL not in sys.path:
    sys.path.insert(0, PASTA_PAINEL)
