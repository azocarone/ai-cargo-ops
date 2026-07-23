import os
import logging
import sys
from dotenv import load_dotenv

# Importaciones de infraestructura y soporte
from modulo.manager_rag import GestorRAG
from modulo.agents_factory import inicializar_agentes
from modulo.builder import crear_grafo_deporca


# =====================================================================
# CONFIGURACIÓN INICIAL DEL ENTORNO Y LOGS
# =====================================================================
def inicializar_entorno():
    """Carga las variables de entorno y configura el sistema de logging."""
    load_dotenv()

    nivel_env = os.environ.get("LOG_LEVEL", "INFO").upper()
    niveles_validos = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    nivel_logging = niveles_validos.get(nivel_env, logging.INFO)

    logging.basicConfig(
        level=nivel_logging,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    return logging.getLogger("main")


# =====================================================================
# FLUJO PRINCIPAL
# =====================================================================
def main():
    # Inicialización del Logger de la app
    logger = inicializar_entorno()
    logger.info("Iniciando entorno multi-agente de producción...")

    # Evaluación de forma segura, bandera de desarrollo
    modo_dev = os.environ.get("MODO_DESARROLLO", "False").lower() in ("true", "1", "t")

    # -----------------------------------------------------------------
    # PASO 1: Inicialización del RAG con la clase GestorRAG
    # -----------------------------------------------------------------
    logger.info("Configurando el ecosistema RAG global...")
    
    rag = GestorRAG(ruta_assets="./assets")
    # Genera los embeddings levanta la base vectorial FAISS en memoria
    retriever_compartido = rag.inicializar_base_vectores()

    # -----------------------------------------------------------------
    # PASO 2: Instanciación de los Agentes mediante Polimorfismo
    # -----------------------------------------------------------------
    logger.info("Instanciando la jerarquía de agentes...")

    # Puebla el diccionario AGENTES
    inicializar_agentes(modo_dev, retriever_compartido)

    # -----------------------------------------------------------------
    # PASO 3: Implementación del Sistema Multi-Agente con LangGraph
    # -----------------------------------------------------------------

    # Compilar el grafo modularizado
    app = crear_grafo_deporca()

    pregunta = (
        "Hola, requiero exportar 3 contenedores en un mismo booking desde Valencia hacia el puerto. "
        "Además, uno de ellos tiene una factura con 5 ítems de clasificación arancelaria compleja. "
        "¿Cuánto me costaría el agenciamiento, la DUA y el transporte? ¿Puedo pagar en bolívares?"
    )

    estado_inicial = {
        "pregunta_usuario": pregunta,
        "payload_orquestador": None,
        "respuesta_auditor": None,
        "respuesta_financiero": None,
        "respuesta_bot": None,
        "respuesta_final": ""
    }

    # Invocación del sistema multi-agente
    resultado = app.invoke(estado_inicial)

    print("\n--- RESUMEN FINAL ---")
    print(resultado["respuesta_final"])

if __name__ == "__main__":
    main()