"""Paquete de Interfaces de Usuario para el sistema DEPORCA.

Este módulo (`ui/__init__.py`) actúa como la fachada y punto de entrada unificado
del paquete de UI, reexportando las representaciones de interfaz de usuario
(CLI y Web) desacopladas de la lógica de negocio central del sistema.

Módulos Reexportados:
    InterfazCLI: Clase para la interfaz de línea de comandos enriquecida (Rich).
    InterfazWebStreamlit: Clase para la interfaz web interactiva (Streamlit).

Usage:
    >>> from ui import InterfazCLI, InterfazWebStreamlit
"""

# Importaciones relativas explícitas para asegurar la portabilidad dentro del paquete
from .cli_rich import InterfazCLI
from .web import InterfazWebStreamlit

# Definición explícita e inmutable de la API pública expuesta por el paquete
__all__: list[str] = [
    "InterfazCLI",
    "InterfazWebStreamlit",
]