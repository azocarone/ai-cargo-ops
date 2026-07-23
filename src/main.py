import os
import logging
import sys
from dotenv import load_dotenv

# Importaciones de soporte e infraestructura
from modulo.manager_rag import GestorRAG
from modulo.prompts import PROMPT_ORQUESTADOR, PROMPT_AUDITOR, PROMPT_FINANCIERO, PROMPT_BOT
from modulo.schemes import OrquestadorAgentResponse, AuditorAgentResponse, FinancieroAgentResponse, BotAgentResponse

# Importaciones de agentes polimórficos
from modulo.agent_direct import AgenteDirecto
from modulo.agent_rag import AgenteRAG


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

    # Evaluación de forma segura la bandera de desarrollo
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

    # Capa Superior: Orquestador (No requiere retriever ya que hereda de AgenteDirecto)
    agent_orquestador = AgenteDirecto(
        prompt_sistema=PROMPT_ORQUESTADOR,
        esquema_respuesta=OrquestadorAgentResponse,
        nombre_agente="Orquestador",
        modo_desarrollo=modo_dev
    )

    # Capa Operativa: Auditor (Requiere retriever e inyecta la lógica RAG)
    agent_auditor = AgenteRAG(
        retriever=retriever_compartido,
        prompt_sistema=PROMPT_AUDITOR,
        esquema_respuesta=AuditorAgentResponse,
        nombre_agente="Auditor",
        modo_desarrollo=modo_dev
    )

    # Capa Operativa: Financiero (Reutiliza el mismo retriever compartido)
    agent_financiero = AgenteRAG(
        retriever=retriever_compartido,
        prompt_sistema=PROMPT_FINANCIERO,
        esquema_respuesta=FinancieroAgentResponse,
        nombre_agente="Financiero",
        modo_desarrollo=modo_dev
    )

    # Capa Operativa: Bot (No requiere retriever ya que hereda de AgenteDirecto)
    agent_bot = AgenteDirecto(
        prompt_sistema=PROMPT_BOT,
        esquema_respuesta=BotAgentResponse,
        nombre_agente="Bot",
        modo_desarrollo=modo_dev
    )

    # -----------------------------------------------------------------
    # PASO 3: Implementación del Sistema Multi-Agente con LangGraph
    # -----------------------------------------------------------------
    from modulo.builder import crear_grafo_deporca

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