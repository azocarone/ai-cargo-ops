import os
import logging
import sys
from dotenv import load_dotenv

# Importaciones de soporte e infraestructura
from modulo.gestor_rag import GestorRAG
from modulo.prompts import PROMPT_ORQUESTADOR, PROMPT_AUDITOR, PROMPT_FINANCIERO, PROMPT_BOT
from modulo.esquemas import OrquestadorAgentResponse, AuditorAgentResponse, FinancieroAgentResponse, BotAgentResponse

# Importaciones de agentes polimórficos
from modulo.agente_directo import AgenteDirecto
from modulo.agente_rag import AgenteRAG


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

    # 3.1.: Mapeo del Estado Global del Grafo (State)
    from typing import TypedDict, List, Optional, Annotated
    import operator

    # Definición del Estado Centralizado
    class EstadoMultiAgente(TypedDict):
        # Entrada inicial del usuario
        pregunta_usuario: str
        
        # Salida parseada del Orquestador
        payload_orquestador: Optional[OrquestadorAgentResponse]
        
        # Respuestas individuales de los subagentes (acumulativas mediante operator.add)
        respuesta_auditor: Optional[AuditorAgentResponse]
        respuesta_financiero: Optional[FinancieroAgentResponse]
        respuesta_bot: Optional[BotAgentResponse]
        
        # Consolidado final para presentar al usuario
        respuesta_final: str

    # 3.2.: Definición de los Nodos del Grafo (Nodes)

    # ---------------------------------------------------------------------
    # NODO 1: ORQUESTADOR
    # ---------------------------------------------------------------------
    def nodo_orquestador(state: EstadoMultiAgente) -> dict:
        pregunta = state["pregunta_usuario"]
        # Invocación directa usando la instanciación existente
        res_orquestador: OrquestadorAgentResponse = agent_orquestador.consultar(pregunta)
        
        return {"payload_orquestador": res_orquestador}

    # ---------------------------------------------------------------------
    # NODO 2: AUDITOR
    # ---------------------------------------------------------------------
    def nodo_auditor(state: EstadoMultiAgente) -> dict:
        payload = state["payload_orquestador"]
        
        # Extraemos el fragmento de texto asignado específicamente al auditor
        contexto_especifico = next(
            (item.contexto_agente for item in payload.agentes_activados if item.agente == "auditor"),
            state["pregunta_usuario"]
        )
        
        res_auditor: AuditorAgentResponse = agent_auditor.consultar(contexto_especifico)
        return {"respuesta_auditor": res_auditor}

    # ---------------------------------------------------------------------
    # NODO 3: FINANCIERO
    # ---------------------------------------------------------------------
    def nodo_financiero(state: EstadoMultiAgente) -> dict:
        payload = state["payload_orquestador"]
        
        contexto_especifico = next(
            (item.contexto_agente for item in payload.agentes_activados if item.agente == "financiero"),
            state["pregunta_usuario"]
        )
        
        res_financiero: FinancieroAgentResponse = agent_financiero.consultar(contexto_especifico)
        return {"respuesta_financiero": res_financiero}

    # ---------------------------------------------------------------------
    # NODO 4: BOT
    # ---------------------------------------------------------------------
    def nodo_bot(state: EstadoMultiAgente) -> dict:
        payload = state["payload_orquestador"]
        
        contexto_especifico = next(
            (item.contexto_agente for item in payload.agentes_activados if item.agente == "bot"),
            state["pregunta_usuario"]
        )
        
        res_bot: BotAgentResponse = agent_bot.consultar(contexto_especifico)
        return {"respuesta_bot": res_bot}

    # ---------------------------------------------------------------------
    # NODO 5: SINTETIZADOR / CONSOLIDADOR
    # ---------------------------------------------------------------------
    def nodo_sintetizador(state: EstadoMultiAgente) -> dict:
        """Unifica las salidas estructuradas recibidas de los subagentes."""
        partes_respuesta = []
        
        if state.get("respuesta_bot"):
            bot_res = state["respuesta_bot"]
            partes_respuesta.append(f"🤖 **Asistente:** {bot_res.mensaje}")
            
        if state.get("respuesta_auditor"):
            auditor_res = state["respuesta_auditor"]
            partes_respuesta.append(f"📋 **Dictamen Operativo/Auditoría:**\n{auditor_res.respuesta_directa}")
            if auditor_res.responsable_operativo:
                partes_respuesta.append(f"_Responsable Operativo:_ {auditor_res.responsable_operativo}")
                
        if state.get("respuesta_financiero"):
            fin_res = state["respuesta_financiero"]
            partes_respuesta.append(f"💰 **Cotización y Finanzas:**\n{fin_res.respuesta_cliente}")
        
        consolidado = "\n\n---\n\n".join(partes_respuesta)
        return {"respuesta_final": consolidado}

    # 3.3.: Lógica de Enrutamiento Dinámico (Conditional Edges)
    def ruteador_orquestador(state: EstadoMultiAgente) -> List[str]:
        payload = state.get("payload_orquestador")
        
        if not payload or not payload.agentes_activados:
            # Por defecto, si no hay clasificación, enviamos al Bot
            return ["nodo_bot"]
        
        # Mapeo del esquema Pydantic a los nombres de los nodos en LangGraph
        mapa_nodos = {
            "auditor": "nodo_auditor",
            "financiero": "nodo_financiero",
            "bot": "nodo_bot"
        }
        
        nodos_destino = [
            mapa_nodos[item.agente] 
            for item in payload.agentes_activados 
            if item.agente in mapa_nodos
        ]
        
        return nodos_destino

    # 3.4.: Ensamblado e Construcción del Grafo (StateGraph)
    from langgraph.graph import StateGraph, START, END

    # 1. Inicializar el grafo con el esquema de estado
    builder = StateGraph(EstadoMultiAgente)

    # 2. Agregar los nodos al grafo
    builder.add_node("nodo_orquestador", nodo_orquestador)
    builder.add_node("nodo_auditor", nodo_auditor)
    builder.add_node("nodo_financiero", nodo_financiero)
    builder.add_node("nodo_bot", nodo_bot)
    builder.add_node("nodo_sintetizador", nodo_sintetizador)

    # 3. Punto de entrada
    builder.add_edge(START, "nodo_orquestador")

    # 4. Enrutamiento Condicional Dinámico (Fan-out)
    builder.add_conditional_edges(
        "nodo_orquestador",
        ruteador_orquestador,
        {
            "nodo_auditor": "nodo_auditor",
            "nodo_financiero": "nodo_financiero",
            "nodo_bot": "nodo_bot"
        }
    )

    # 5. Convergencia hacia el Sintetizador (Fan-in)
    builder.add_edge("nodo_auditor", "nodo_sintetizador")
    builder.add_edge("nodo_financiero", "nodo_sintetizador")
    builder.add_edge("nodo_bot", "nodo_sintetizador")

    # 6. Salida del sistema
    builder.add_edge("nodo_sintetizador", END)

    # 7. Compilar el grafo ejecutable
    grafo_deporca = builder.compile()

    # 3.5.: Ejecución End-to-End

    pregunta_ejemplo = (
    "Hola, requiero exportar 3 contenedores en un mismo booking desde Valencia hacia el puerto. "
    "Además, uno de ellos tiene una factura con 5 ítems de clasificación arancelaria compleja. "
    "¿Cuánto me costaría el agenciamiento, la DUA y el transporte? ¿Puedo pagar en bolívares?"
    )

    # Estado inicial
    estado_inicial = {
        "pregunta_usuario": pregunta_ejemplo,
        "payload_orquestador": None,
        "respuesta_auditor": None,
        "respuesta_financiero": None,
        "respuesta_bot": None,
        "respuesta_final": ""
    }

    # Invocación del grafo
    resultado = grafo_deporca.invoke(estado_inicial)

    # Resultado final
    print(resultado["respuesta_final"])

if __name__ == "__main__":
    main()