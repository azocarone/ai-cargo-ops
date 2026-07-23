"""
nodes.py - Etapa 2: Definición de los Nodos del Grafo (Nodes)
"""
from modulo.state import EstadoMultiAgente
from modulo.schemes import (
    OrquestadorAgentResponse,
    AuditorAgentResponse,
    FinancieroAgentResponse,
    BotAgentResponse
)

# Importamos directamente el diccionario de agentes
from modulo.agents_factory import AGENTS


def nodo_orquestador(state: EstadoMultiAgente) -> dict:
    """Procesa la entrada del usuario y extrae metadatos/enrutamiento."""
    pregunta = state["pregunta_usuario"]
    res_orquestador: OrquestadorAgentResponse = AGENTS["orquestador"].consultar(pregunta)
    return {"payload_orquestador": res_orquestador}


def nodo_auditor(state: EstadoMultiAgente) -> dict:
    """Ejecuta el Agente Auditor sobre su contexto asignado."""
    payload = state["payload_orquestador"]
    contexto_especifico = next(
        (item.contexto_agente for item in payload.agentes_activados if item.agente == "auditor"),
        state["pregunta_usuario"]
    )
    res_auditor: AuditorAgentResponse = AGENTS["auditor"].consultar(contexto_especifico)
    return {"respuesta_auditor": res_auditor}


def nodo_financiero(state: EstadoMultiAgente) -> dict:
    """Ejecuta el Agente Financiero sobre su contexto asignado."""
    payload = state["payload_orquestador"]
    contexto_especifico = next(
        (item.contexto_agente for item in payload.agentes_activados if item.agente == "financiero"),
        state["pregunta_usuario"]
    )
    res_financiero: FinancieroAgentResponse = AGENTS["financiero"].consultar(contexto_especifico)
    return {"respuesta_financiero": res_financiero}


def nodo_bot(state: EstadoMultiAgente) -> dict:
    """Ejecuta el Agente Bot sobre su contexto asignado."""
    payload = state["payload_orquestador"]
    contexto_especifico = next(
        (item.contexto_agente for item in payload.agentes_activados if item.agente == "bot"),
        state["pregunta_usuario"]
    )
    res_bot: BotAgentResponse = AGENTS["bot"].consultar(contexto_especifico)
    return {"respuesta_bot": res_bot}


def nodo_sintetizador(state: EstadoMultiAgente) -> dict:
    """Unifica las salidas estructuradas recibidas de los subagentes ejecutados."""
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