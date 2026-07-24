"""Módulo de entrada principal para el sistema multi-agente de DEPORCA.

Este módulo se limita a coordinar la inicialización del entorno, cargar
los componentes pesados (RAG, Agentes y Grafo) e invocar la interfaz de
usuario seleccionada (CLI).
"""

import logging
import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

# Importaciones de infraestructura local
from modulo.agents_factory import inicializar_agentes
from modulo.builder import crear_grafo_deporca
from modulo.manager_rag import GestorRAG

# Importación de la nueva interfaz de usuario
from ui import InterfazCLI

# =====================================================================
# CONFIGURACIÓN DEL ENTORNO Y LOGS
# =====================================================================

def inicializar_entorno() -> logging.Logger:
    """Carga variables de entorno y configura el sistema de logging centralizado."""
    load_dotenv()

    nivel_env: str = os.environ.get("LOG_LEVEL", "INFO").upper()
    niveles_validos: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    nivel_logging: int = niveles_validos.get(nivel_env, logging.INFO)

    logging.basicConfig(
        level=nivel_logging,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    return logging.getLogger("main")


# =====================================================================
# FLUJO PRINCIPAL
# =====================================================================

def main() -> None:
    """Bootsztrapea el sistema e inicia la interfaz por consola."""
    logger: logging.Logger = inicializar_entorno()
    logger.info("Iniciando entorno multi-agente de producción...")

    # Evaluación de bandera de desarrollo
    modo_dev: bool = os.environ.get("MODO_DESARROLLO", "False").lower() in (
        "true",
        "1",
        "t",
    )

    # 1. Configuración del subsistema RAG
    logger.info("Configurando el ecosistema RAG global...")
    rag: GestorRAG = GestorRAG(ruta_assets="./assets")
    retriever_compartido: Any = rag.inicializar_base_vectores()

    # 2. Instanciación de Agentes
    logger.info("Instanciando la jerarquía de agentes...")
    agentes_instanciados: Dict[str, Any] = inicializar_agentes(
        modo_dev, retriever_compartido
    )

    # 3. Compilación del Grafo LangGraph
    logger.info("Compilando Grafo de LangGraph...")
    app_grafo = crear_grafo_deporca()

    # 4. Transferencia del control a la Interfaz CLI
    cli = InterfazCLI(app_grafo=app_grafo, agentes=agentes_instanciados)
    cli.iniciar()


if __name__ == "__main__":
    main()