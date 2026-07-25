"""Punto de entrada principal para la interfaz web de Streamlit en DEPORCA.

Este módulo se encarga de la orquestación inicial del sistema. Configura e
instancia la infraestructura central (RAG, Agentes y Grafo de workflow)
utilizando el decorador de caché de Streamlit (`@st.cache_resource`) para
evitar re-computaciones costosas entre recargas de la UI.

Además, implementa resolución dinámica de rutas ancladas a la raíz del
proyecto, permitiendo flexibilidad mediante variables de entorno.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Tuple

import streamlit as st
from dotenv import load_dotenv

# Importaciones de módulos internos
from modulo.agents_factory import inicializar_agentes
from modulo.builder import crear_grafo_deporca
from modulo.manager_rag import GestorRAG
from ui import InterfazWebStreamlit

# -----------------------------------------------------------------------------
# ANCLA DE RUTAS DEL PROYECTO (PEP 8 / pathlib)
# -----------------------------------------------------------------------------
# Definimos la raíz del proyecto retrocediendo dinámicamente desde la ubicación
# de este archivo (`src/main_web.py` -> `src/` -> RAÍZ). Esto elimina la
# dependencia del directorio de trabajo actual (CWD) al ejecutar la aplicación.
BASE_DIR: Path = Path(__file__).resolve().parent.parent


@st.cache_resource
def cargar_infraestructura_sistema() -> Tuple[Any, Dict[str, Any]]:
    """Inicializa y almacena en caché la infraestructura pesada del sistema.

    Carga las variables de entorno, configura el logging y resuelve de forma
    infalible la ruta del directorio de recursos (`assets`) anclándola a `BASE_DIR`.
    A continuación, inicializa la base vectorial RAG, instancía la fábrica de
    agentes y compila el grafo de orquestación.

    Returns:
        Tuple[Any, Dict[str, Any]]:
            - app_grafo: Instancia ejecutable del grafo de flujo/orquestación.
            - agentes_instanciados: Diccionario con los agentes del sistema.

    Raises:
        FileNotFoundError: Si la ruta configurada para assets no existe en el sistema.
    """
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    # Evaluación booleana flexible del modo desarrollo
    modo_dev: bool = os.environ.get("MODO_DESARROLLO", "False").lower() in (
        "true",
        "1",
        "t",
    )

    # 1. RESOLUCIÓN DE RUTAS Y CONFIGURACIÓN RAG
    # Garantiza tolerancia a cambios en el archivo .env o variaciones en la estructura de carpetas
    nombre_carpeta_env: str = os.environ.get("ASSETS_PATH", "assets")
    ruta_assets: Path = (BASE_DIR / nombre_carpeta_env).resolve()

    # Programación defensiva: Previene fallos en cascada dentro de GestorRAG si la carpeta no existe
    if not ruta_assets.exists():
        logging.error("No se encontró el directorio de assets en: %s", ruta_assets)
        raise FileNotFoundError(
            f"El directorio configurado para assets no existe: {ruta_assets}\n"
            "Verifica la variable ASSETS_PATH en tu archivo .env o asegura "
            "que la carpeta exista en la raíz del proyecto."
        )

    rag = GestorRAG(ruta_assets=str(ruta_assets))
    retriever_compartido = rag.inicializar_base_vectores()

    # 2. INSTANCIACIÓN DE AGENTES E INYECCIÓN DE DEPENDENCIAS
    agentes_instanciados = inicializar_agentes(modo_dev, retriever_compartido)

    # 3. CONSTRUCCIÓN Y COMPILACIÓN DEL GRAFO DE ORQUESTACIÓN
    app_grafo = crear_grafo_deporca()

    return app_grafo, agentes_instanciados


def main() -> None:
    """Punto de entrada principal que inicializa y renderiza la interfaz gráfica."""
    app_grafo, agentes = cargar_infraestructura_sistema()
    interfaz = InterfazWebStreamlit(app_grafo=app_grafo, agentes=agentes)
    interfaz.renderizar()


if __name__ == "__main__":
    main()