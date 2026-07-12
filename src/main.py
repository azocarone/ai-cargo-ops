"""
Script principal para la ejecución y prueba del motor RAG de DEPORCA.

Este módulo actúa como el punto de entrada (Entrypoint) de la aplicación. Se encarga de
cargar las variables de entorno locales, inicializar el cliente del Modelo de Lenguaje (LLM) 
a través de la infraestructura de NVIDIA NIM y realizar una consulta de prueba.

================================================================================
PRERREQUISITOS (DEPENDENCIAS)
================================================================================
Instale las librerías necesarias en su entorno virtual antes de ejecutar:
    $ pip install -qU python-dotenv
    $ pip install -qU langchain-nvidia-ai-endpoints
    $ pip install -qU langchain

================================================================================
INSTRUCCIONES DE EJECUCIÓN
================================================================================
1. Asegúrese de tener un archivo `.env` en la raíz con la credencial `NVIDIA_API_KEY`.
2. Ejecute el script desde la raíz del proyecto:
    $ python main.py
"""

from dotenv import load_dotenv
from modulo.configuracion_llm_nvidia import ConfiguracionLLMNvidia

load_dotenv()

instance_llm = ConfiguracionLLMNvidia(modo_desarrollo=True)
# instance_llm.info()
llm = instance_llm.obtener_llm()

# respuesta = llm.invoke("¿Qué es el RAG en Inteligencia Artificial?")
# print("\nRespuesta de prueba:", respuesta.content)