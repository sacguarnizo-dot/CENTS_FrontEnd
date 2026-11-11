"""
Módulo de Pantallas y Vistas de CENTS
"""
import os
import sys

_directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _directorio_raiz not in sys.path:
    sys.path.insert(0, _directorio_raiz)
