"""Site do Orzy (fase 3). Ver docs/07-fase-3-plano.md e web/LEIA-ME.md.

O programa do PC (painel-ml/) não é um pacote Python. Este arquivo põe a pasta dele no caminho de busca,
para o site usar as mesmas regras (analise.py) e a mesma coleta (meus_anuncios.py) sem copiar código.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "painel-ml"))
