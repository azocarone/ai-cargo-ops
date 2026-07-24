"""Paquete de Interfaces de Usuario para el sistema DEPORCA.

Este paquete agrupa las distintas representaciones de interfaz (CLI, API, Web)
desacopladas de la lógica central del sistema.
"""

from ui.cli import InterfazCLI

# Define explícitamente qué símbolos se exportan cuando alguien usa `from ui import *`
__all__ = ["InterfazCLI"]