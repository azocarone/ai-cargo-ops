"""Módulo de entrada principal para el sistema multi-agente de DEPORCA.

Este módulo se encarga de bootstrapear el entorno de ejecución, cargar las
variables de entorno, configurar el registro de eventos (logging), instanciar los
recursos compartidos (como el motor RAG) y compilar el grafo de ejecucion de
LangGraph para gestionar la interacción en bucle interactivo con el usuario.
"""

import logging
import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

# Importaciones de infraestructura local y componentes del sistema
from modulo.agents_factory import inicializar_agentes
from modulo.builder import crear_grafo_deporca
from modulo.manager_rag import GestorRAG

# =====================================================================
# CONFIGURACIÓN INICIAL DEL ENTORNO Y LOGGING
# =====================================================================

def inicializar_entorno() -> logging.Logger:
    """Carga variables de entorno y configura el sistema centralizado de logs.

    Mapea el nivel de log definido en las variables de entorno (`LOG_LEVEL`)
    hacia la configuración nativa de Python. Si la variable no existe o no es
    válida, aplica `INFO` por defecto.

    Returns:
        logging.Logger: Objeto logger configurado para el canal principal del módulo.
    """
    load_dotenv()

    nivel_env: str = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Mapeo explícito de cadenas a constantes de logging para evitar fallos por valores inválidos
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
# FLUJO PRINCIPAL Y BUCLE DE INTERACCIÓN
# =====================================================================

def main() -> None:
    """Ejecuta la orquestación principal del sistema multi-agente DEPORCA.

    Realiza el arranque secuencial del sistema:
    1. Configuración de logging y lectura de flags del entorno.
    2. Inicialización del motor RAG y generación/recuperación del retriever.
    3. Construcción del mapa de agentes según el modo de entorno (dev/prod).
    4. Compilación del grafo de LangGraph.
    5. Entrada en el bucle interactivo de entrada/salida para el usuario (CLI).
    """
    logger: logging.Logger = inicializar_entorno()
    logger.info("Iniciando entorno multi-agente de producción...")

    # Coerción segura de variable de entorno booleana para activar el modo de desarrollo
    modo_dev: bool = os.environ.get("MODO_DESARROLLO", "False").lower() in (
        "true",
        "1",
        "t",
    )

    # -----------------------------------------------------------------
    # PASO 1: Inicialización del subsistema RAG
    # -----------------------------------------------------------------
    logger.info("Configurando el ecosistema RAG global...")
    rag: GestorRAG = GestorRAG(ruta_assets="./assets")
    
    # Genera los embeddings y carga en memoria el retriever vectorial (e.g., FAISS)
    retriever_compartido: Any = rag.inicializar_base_vectores()

    # -----------------------------------------------------------------
    # PASO 2: Instanciación de Agentes
    # -----------------------------------------------------------------
    logger.info("Instanciando la jerarquía de agentes...")
    agentes_instanciados: Dict[str, Any] = inicializar_agentes(
        modo_dev, retriever_compartido
    )

    # -----------------------------------------------------------------
    # PASO 3: Compilación e Invocación del Grafo Multi-Agente (LangGraph)
    # -----------------------------------------------------------------
    app = crear_grafo_deporca()

    print("=== Sistema Multi-Agente DEPORCA Activo ===")
    print("Escribe 'salir' para terminar la conversación.\n")

    # Bucle interactivo REPL (Read-Eval-Print Loop)
    while True:
        pregunta: str = input("Ingresa tu consulta: ").strip()

        # Evaluación de la cláusula de parada del bucle
        if pregunta.lower() in ("salir", "exit", "quit"):
            print("\n¡Hasta luego!")
            break

        # Saneamiento básico de entradas vacías
        if not pregunta:
            print("Por favor, ingresa una pregunta válida.\n")
            continue

        # Estructura del estado inicial del grafo requerida por LangGraph
        estado_inicial: Dict[str, Any] = {
            "pregunta_usuario": pregunta,
            "agentes": agentes_instanciados,
            "payload_orquestador": None,
            "respuesta_auditor": None,
            "respuesta_financiero": None,
            "respuesta_bot": None,
            "respuesta_final": "",
        }

        # Transferencia de control al orquestador del grafo
        resultado: Dict[str, Any] = app.invoke(estado_inicial)

        print("\n--- RESUMEN FINAL ---")
        print(resultado.get("respuesta_final", "Sin respuesta generada."))
        print("\n" + "=" * 40 + "\n")


if __name__ == "__main__":
    main()