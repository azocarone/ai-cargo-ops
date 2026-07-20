import os
import logging
import sys
from dotenv import load_dotenv

# 1. Esquemas y Prompts de tu módulo original
from modulo.esquemas import OrquestadorAgentResponse, AuditorAgentResponse, FinancieroAgentResponse
from modulo.prompts import PROMPT_ORQUESTADOR, PROMPT_AUDITOR, PROMPT_FINANCIERO

# 2. Importamos las dos subclases que aplican Polimorfismo
from modulo.agente_rag import AgenteRAG          # Para el Auditor (Con RAG)
from modulo.agente_directo import AgenteDirecto  # Para el Orquestador (Sin RAG)


# =====================================================================
# CONFIGURACIÓN INICIAL DEL ENTORNO Y LOGS
# =====================================================================
def inicializar_entorno():
    """Carga las variables de entorno y configura el sistema de logging."""
    # 1. Cargar el archivo .env antes de cualquier otra cosa
    load_dotenv()

    # 2. Leer el nivel de verbosidad (por defecto INFO)
    nivel_env = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Mapear el string del .env a las constantes numéricas de la librería logging
    # Si ponen un nivel inválido en el .env, por seguridad cae en INFO
    niveles_validos = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    nivel_logging = niveles_validos.get(nivel_env, logging.INFO)

    # 3. Configurar el logging global de la aplicación
    logging.basicConfig(
        level=nivel_logging,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Retornamos un logger para el archivo main
    return logging.getLogger("main")


# =====================================================================
# SIMULACIÓN DEL RETRIEVER PARA EL AGENTE RAG (MOCK)
# =====================================================================
class MockRetriever:
    def invoke(self, query: str):
        from langchain_core.documents import Document
        return [
            Document(
                page_content="Normativa DEPORCA: Las auditorías se ejecutan de forma trimestral.",
                metadata={"source": "/rutas/manuales/Manual_Auditoria_V2.pdf"}
            )
        ]


# =====================================================================
# FLUJO PRINCIPAL (MAIN)
# =====================================================================
def main():
    # Inicializamos todo al arrancar y obtenemos el logger principal
    logger = inicializar_entorno()
    logger.info("Entorno y logs inicializados correctamente.")
    logger.info("Iniciando entorno multi-agente polimórfico...")

    # Componentes de inicialización
    retriever_faiss = MockRetriever()
    modo_dev = True

    # -----------------------------------------------------------------
    # CREACIÓN DE INSTANCIAS (Aquí se aprecia el polimorfismo)
    # -----------------------------------------------------------------
    logger.info("Instanciando agentes desde la misma base...")

    # El Orquestador es un 'AgenteDirecto' (Usa la base común pero redefine el payload y el prompt)
    orquestador = AgenteDirecto(
        prompt_sistema=PROMPT_ORQUESTADOR,
        esquema_respuesta=OrquestadorAgentResponse,
        nombre_agente="Orquestador",
        modo_desarrollo=modo_dev
    )

    # El Auditor es un 'AgenteRAG' (Usa la base común pero inyecta la búsqueda en FAISS)
    agente_auditor = AgenteRAG(
        retriever=retriever_faiss,
        prompt_sistema=PROMPT_AUDITOR,
        esquema_respuesta=AuditorAgentResponse,
        nombre_agente="Auditor",
        modo_desarrollo=modo_dev
    )

    # El Auditor es un 'AgenteRAG' (Usa la base común pero inyecta la búsqueda en FAISS)
    agente_financiero = AgenteRAG(
        retriever=retriever_faiss,
        prompt_sistema=PROMPT_FINANCIERO,
        esquema_respuesta=FinancieroAgentResponse,
        nombre_agente="Financiero",
        modo_desarrollo=modo_dev
    )

    # -----------------------------------------------------------------
    # EJECUCIÓN (Interfaz idéntica gracias al Polimorfismo)
    # -----------------------------------------------------------------
    
    print("\n" + "="*60 + "\n   EJECUTANDO: ORQUESTADOR (Polimorfismo Directo)\n" + "="*60)
    pregunta_orquestador = "Quiero auditar el inventario y revisar las finanzas."
    
    # Llama a .consultar(). Internamente ejecuta el _preparar_payload de AgenteDirecto
    respuesta_orq: OrquestadorAgentResponse = orquestador.consultar(pregunta_orquestador)
    print(f"\n[Respuesta Orquestador]: {respuesta_orq}")


    print("\n" + "="*60 + "\n   EJECUTANDO: AUDITOR (Polimorfismo RAG)\n" + "="*60)
    pregunta_auditor = "¿Cada cuánto se hacen las auditorías?"
    
    # Llama al MISMO método .consultar(). Internamente ejecuta el _preparar_payload de AgenteRAG
    respuesta_aud: AuditorAgentResponse = agente_auditor.consultar(pregunta_auditor)
    print(f"\n[Respuesta Auditor]: {respuesta_aud}")


    print("\n" + "="*60 + "\n   EJECUTANDO: FINANCIERO (Polimorfismo RAG)\n" + "="*60)
    pregunta_financiero = "¿Cada cuánto se hacen las auditorías?"
        
    # Llama al MISMO método .consultar(). Internamente ejecuta el _preparar_payload de AgenteRAG
    respuesta_fin: FinancieroAgentResponse = agente_financiero.consultar(pregunta_financiero)
    print(f"\n[Respuesta Financiero]: {respuesta_fin}")

    logger.info("Todos los agentes respondieron correctamente.")

if __name__ == "__main__":
    main()