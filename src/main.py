"""Módulo de entrada principal para la interfaz CLI del sistema multi-agente DEPORCA.

Este módulo actúa como el orquestador del arranque (bootstrap) de la aplicación,
garantizando una secuencia clara de inicialización mediante Inyección de Dependencias
y configuración de variables de entorno globales.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Final

from dotenv import load_dotenv

from modulo.agents_factory import inicializar_agentes
from modulo.builder import crear_grafo_deporca
from modulo.manager_rag import GestorRAG
from ui import InterfazCLI

# Anclaje de la raíz del proyecto para asegurar la resolución absoluta de rutas
# independientemente del directorio actual de trabajo (CWD).
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent

# Mapeo explicito de niveles de log segun standard PEP 8 / logging
_NIVELES_LOGGING: Final[Dict[str, int]] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def inicializar_entorno() -> logging.Logger:
    """Carga las variables de entorno y configura el logger centralizado.

    Lee las variables presentes en el archivo `.env` y establece el nivel
    de registro del sistema. Si el nivel no es especificado o es inválido,
    se aplica `logging.INFO` como salvaguarda.

    Returns:
        logging.Logger: Instancia del registrador principal ('main') configurado.
    """
    load_dotenv()

    # Normalización a mayúsculas para evitar incoherencias por casing en el `.env`
    nivel_env: str = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Mapeo defensivo: evita KeyError si el usuario define un nivel no válido
    nivel_logging: int = _NIVELES_LOGGING.get(nivel_env, logging.INFO)

    logging.basicConfig(
        level=nivel_logging,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    return logging.getLogger("main")


def main() -> None:
    """Orquesta la secuencia de arranque del sistema y cede el control a la CLI.

    Flujo de Inyección de Dependencias:
    1. Carga de variables y logging.
    2. Validación de sistema de archivos y motor RAG.
    3. Construcción de jerarquía de agentes.
    4. Compilación del grafo de estados (LangGraph).
    5. Delegación a la interfaz de usuario.

    Raises:
        FileNotFoundError: Si la ruta configurada en ASSETS_PATH no existe.
    """
    logger: logging.Logger = inicializar_entorno()
    logger.info("Iniciando entorno multi-agente de producción (CLI)...")

    # Evaluación booleana permisiva para flags de entorno
    modo_dev: bool = os.environ.get("MODO_DESARROLLO", "False").lower() in (
        "true",
        "1",
        "t",
    )

    # -------------------------------------------------------------------------
    # 1. Configuración de Assets y Subsistema RAG
    # -------------------------------------------------------------------------
    logger.info("Configurando el ecosistema RAG global...")
    nombre_carpeta_env: str = os.environ.get("ASSETS_PATH", "assets")
    ruta_assets: Path = (BASE_DIR / nombre_carpeta_env).resolve()

    # Programación defensiva: falla rápido (fail-fast) si falta un recurso esencial
    if not ruta_assets.exists():
        logger.error("Error crítico: No se encontró el directorio de assets en: %s", ruta_assets)
        raise FileNotFoundError(
            f"El directorio configurado para assets no existe: {ruta_assets}\n"
            "Verifica la variable ASSETS_PATH en tu archivo .env o asegura "
            "que la carpeta exista en la raíz del proyecto."
        )

    rag: GestorRAG = GestorRAG(ruta_assets=str(ruta_assets))
    retriever_compartido: Any = rag.inicializar_base_vectores()

    # -------------------------------------------------------------------------
    # 2. Instanciación e Inyección de Agentes
    # -------------------------------------------------------------------------
    logger.info("Instanciando la jerarquía de agentes...")
    agentes_instanciados: Dict[str, Any] = inicializar_agentes(
        modo_dev, retriever_compartido
    )

    # -------------------------------------------------------------------------
    # 3. Compilación de Grafo y Ejecución de CLI
    # -------------------------------------------------------------------------
    logger.info("Compilando Grafo de LangGraph...")
    app_grafo: Any = crear_grafo_deporca()

    cli: InterfazCLI = InterfazCLI(app_grafo=app_grafo, agentes=agentes_instanciados)
    cli.iniciar()


if __name__ == "__main__":
    main()