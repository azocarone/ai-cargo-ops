"""
Script principal para la ejecución y prueba del motor RAG de DEPORCA.

Este módulo actúa como el punto de entrada (Entrypoint) de la aplicación. Se encarga de
cargar las variables de entorno locales, inicializar el cliente del Modelo de Lenguaje (LLM) 
a través de la infraestructura de NVIDIA NIM y realizar una consulta de prueba.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from modulo.configuracion_llm_nvidia import ConfiguracionLLMNvidia
from modulo.motor_rag import MotorRAGPrueba

# 1. Cargar el .env para que las variable estén disponibles
load_dotenv()

# 2. Leer el nivel del .env, si no existe, por defecto se usa INFO
nivel_env = os.environ.get("LOG_LEVEL", "INFO").upper()

# 3. Configuración de logs agregando '%(name)s' para visualizar la procedencia del módulo
logging.basicConfig(
    level=getattr(logging, nivel_env, logging.INFO),
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)

# Definir el logger propio para el punto de entrada
logger = logging.getLogger("main")

def main():
    """Función principal que orquesta el ciclo de vida de la aplicación."""
    
    try:
        # 4. Inicializar infraestructura del LLM
        logger.info("Inicializando configuración de NVIDIA NIM...")
        instancia_llm = ConfiguracionLLMNvidia(modo_desarrollo=True)
        
        # Corrección: Llamamos al nuevo método que escribe en logs, no al viejo print
        instancia_llm.registrar_info()
        llm = instancia_llm.obtener_llm()
        
        # 5. Inicializar el motor de pruebas con el LLM inyectado
        rag_testing = MotorRAGPrueba(llm=llm)
        
        # 6. Ejecución de la consulta
        pregunta_prueba = "¿Qué es el RAG en Inteligencia Artificial?"
        respuesta_texto = rag_testing.ejecutar_consulta_lineal(pregunta_prueba)
        
        # Mantenemos el print limpio aquí solo para el reporte final en consola
        print("\n" + "="*60)
        print(f"Respuesta de prueba:\n{respuesta_texto}")
        print("="*60 + "\n")
        
    except Exception as error_contexto:
        logger.critical(f"La aplicación no pudo iniciar correctamente: {error_contexto}")
        sys.exit(1)

if __name__ == "__main__":
    main()