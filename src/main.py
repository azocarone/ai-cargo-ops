"""
Script principal para la ejecución del motor RAG de DEPORCA.

Este módulo actúa como el punto de entrada (Entrypoint) de la aplicación. Se encarga de
cargar las variables de entorno locales, inicializar el cliente del Modelo de Lenguaje (LLM) 
a través de la infraestructura de NVIDIA NIM y realizar una consulta de prueba.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from modulo.gestor_rag import GestorRAG
from modulo.agente_orquestador import AgenteOrquestador
from modulo.agente_auditor import AgenteAuditor
from modulo.test_agentes import test_agente

load_dotenv()

# Leer .env, nivel de verbosidad del log, si no existe, por defecto se usa INFO.
nivel_env = os.environ.get("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, nivel_env, logging.INFO),
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)

# Define el logger propio para el punto de entrada.
logger = logging.getLogger("main")

# ---

def main():
    try:
        # Encender y configurar el RAG global de la aplicación
        rag = GestorRAG(ruta_assets="./assets/")
        retriever_compartido = rag.inicializar_base_vectores()

        #agente_orquestador = AgenteOrquestador(modo_desarrollo=True)
        #test_agente(agente_orquestador)

        agente_auditor = AgenteAuditor(modo_desarrollo=True)
        test_agente(agente_auditor)
        
    except Exception as e:
        logger.critical(f"La aplicación no pudo iniciar correctamente: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()