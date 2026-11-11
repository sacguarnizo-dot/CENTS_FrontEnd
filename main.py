"""
CENTS - Punto de entrada (Redirección a principal.py)
"""
import os
import sys

directorio_base = os.path.dirname(os.path.abspath(__file__))
if directorio_base not in sys.path:
    sys.path.insert(0, directorio_base)

from principal import AplicacionCents

if __name__ == "__main__":
    AplicacionCents().run()
