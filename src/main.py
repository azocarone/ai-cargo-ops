import os
import logging
import sys
from dotenv import load_dotenv

# 1. Importaciones de soporte e infraestructura
from modulo.gestor_rag import GestorRAG
from modulo.esquemas import OrquestadorAgentResponse, AuditorAgentResponse, FinancieroAgentResponse
from modulo.prompts import PROMPT_ORQUESTADOR, PROMPT_AUDITOR, PROMPT_FINANCIERO

# 2. Importaciones de tus agentes polimórficos
from modulo.agente_rag import AgenteRAG
from modulo.agente_directo import AgenteDirecto


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

    # Evaluamos de forma segura la bandera de desarrollo
    modo_dev = os.environ.get("MODO_DESARROLLO", "False").lower() in ("true", "1", "t")

    # -----------------------------------------------------------------
    # PASO 1: Inicialización del RAG Real con tu clase GestorRAG
    # -----------------------------------------------------------------
    logger.info("Configurando el ecosistema RAG global...")
    
    rag = GestorRAG(ruta_assets="./assets")
    # Genera los embeddings de NVIDIA y levanta la base vectorial FAISS en memoria
    retriever_compartido = rag.inicializar_base_vectores()

    # -----------------------------------------------------------------
    # PASO 2: Instanciación de los Agentes mediante Polimorfismo
    # -----------------------------------------------------------------
    logger.info("Instanciando la jerarquía de agentes...")

    # Capa Superior: Orquestador (No requiere retriever ya que hereda de AgenteDirecto)
    orquestador = AgenteDirecto(
        prompt_sistema=PROMPT_ORQUESTADOR,
        esquema_respuesta=OrquestadorAgentResponse,
        nombre_agente="Orquestador",
        modo_desarrollo=modo_dev
    )

    # Capa Operativa: Auditor (Requiere retriever e inyecta la lógica RAG)
    agente_auditor = AgenteRAG(
        retriever=retriever_compartido,
        prompt_sistema=PROMPT_AUDITOR,
        esquema_respuesta=AuditorAgentResponse,
        nombre_agente="Auditor",
        modo_desarrollo=modo_dev
    )

    # Capa Operativa: Financiero (Reutiliza el mismo retriever compartido)
    agente_financiero = AgenteRAG(
        retriever=retriever_compartido,
        prompt_sistema=PROMPT_FINANCIERO,
        esquema_respuesta=FinancieroAgentResponse,
        nombre_agente="Financiero",
        modo_desarrollo=modo_dev
    )

    # -----------------------------------------------------------------
    # PASO 3: Ejecución de Ejemplos
    # -----------------------------------------------------------------
    print("\n" + "="*60 + "\n   PROCESANDO FLUJO DE TRABAJO REAL\n" + "="*60)
    
    pregunta = "Hola, necesito hacer un embarque de 3 contenedores en el mismo booking. ¿Cuánto me costaría el agenciamiento aduanal?"

    # 1. El orquestador atiende al usuario
    # res_orquestador: OrquestadorAgentResponse = orquestador.consultar(pregunta)
    # logger.info("Orquestador analizó con éxito la intención.")

    # Visualizamos los resultados de manera limpia como JSON
    # print("\n[Output Final del Orquestador]:")
    # print(res_orquestador.model_dump_json(indent=4))

    # 2. El auditor ejecuta su flujo con la base FAISS real
    # res_auditor: AuditorAgentResponse = agente_auditor.consultar(pregunta)
    # logger.info("Auditor analizó con éxito la intención.")

    # Visualizamos los resultados de manera limpia como JSON
    # print("\n[Output Final del Auditor]:")
    # print(res_auditor.model_dump_json(indent=4))

    # 3. El financiero ejecuta su flujo con la base FAISS real
    res_financiero: FinancieroAgentResponse = agente_financiero.consultar(pregunta)
    logger.info("Financiero analizó con éxito la intención.")
    
    # Visualizamos los resultados de manera limpia como JSON
    print("\n[Output Final del Financiero]:")
    print(res_financiero.model_dump_json(indent=4))
    

if __name__ == "__main__":
    main()