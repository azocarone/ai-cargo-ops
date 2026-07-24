"""Módulo de Nodos para el Flujo de Trabajo Multi-Agente en LangGraph.

Este módulo define las funciones de procesamiento (nodos) que conforman el grafo
de ejecución multi-agente. Cada nodo interactúa con una instancia de agente
específica, procesa datos dentro del estado compartido (`EstadoMultiAgente`) y
devuelve las actualizaciones pertinentes para el flujo del grafo.

Estructura del Flujo:
    1. `nodo_orquestador`: Analiza la entrada original y define qué agentes activar.
    2. Nodos Especializados (`nodo_auditor`, `nodo_financiero`, `nodo_bot`): Ejecutan
       la tarea del agente asignado extrayendo su contexto del payload del orquestador.
    3. `nodo_sintetizador`: Unifica y consolida las respuestas parciales en un mensaje
       final dirigido al usuario.
"""

from typing import Any, Dict

from modulo.schemes import (
    AuditorAgentResponse,
    BotAgentResponse,
    FinancieroAgentResponse,
    OrquestadorAgentResponse,
)
from modulo.state import EstadoMultiAgente


def nodo_orquestador(state: EstadoMultiAgente) -> Dict[str, Any]:
    """Procesa la pregunta inicial del usuario y enruta la solicitud.

    Obtiene la consulta original y utiliza el agente orquestador para analizar
    la intencionalidad, determinando los subagentes requeridos y el contexto
    específico para cada uno.

    Args:
        state: Estado compartido del grafo que contiene la pregunta y las
            instancias de los agentes.

    Returns:
        Dict[str, Any]: Diccionario con la clave `payload_orquestador` conteniendo
            la estructura `OrquestadorAgentResponse`.
    """
    pregunta: str = state["pregunta_usuario"]
    orquestador = state["agentes"]["orquestador"]

    res_orquestador: OrquestadorAgentResponse = orquestador.consultar(pregunta)
    return {"payload_orquestador": res_orquestador}


def nodo_auditor(state: EstadoMultiAgente) -> Dict[str, Any]:
    """Ejecuta la lógica de negocio asociada al Agente Auditor.

    Busca en el payload del orquestador si existe un contexto/instrucción
    específico para la función de auditoría. De no encontrarlo, utiliza la
    pregunta del usuario como valor de respaldo (fallback).

    Args:
        state: Estado compartido del grafo.

    Returns:
        Dict[str, Any]: Diccionario con la clave `respuesta_auditor` conteniendo
            la respuesta estructurada `AuditorAgentResponse`.
    """
    payload: OrquestadorAgentResponse = state["payload_orquestador"]

    # Búsqueda defensiva mediante un generador y next():
    # Extrae el contexto asignado al rol 'auditor' dentro de 'agentes_activados'.
    # Si el agente no fue explícitamente parametrizado, se degrada elegantemente a la pregunta inicial.
    contexto_especifico: str = next(
        (
            item.contexto_agente
            for item in payload.agentes_activados
            if item.agente == "auditor"
        ),
        state["pregunta_usuario"],
    )
    auditor = state["agentes"]["auditor"]

    res_auditor: AuditorAgentResponse = auditor.consultar(contexto_especifico)
    return {"respuesta_auditor": res_auditor}


def nodo_financiero(state: EstadoMultiAgente) -> Dict[str, Any]:
    """Ejecuta la lógica de negocio asociada al Agente Financiero.

    Extrae los parámetros financieros del payload del orquestador y los envía
    al subagente encargado de análisis de costos o cotizaciones.

    Args:
        state: Estado compartido del grafo.

    Returns:
        Dict[str, Any]: Diccionario con la clave `respuesta_financiero` conteniendo
            la respuesta estructurada `FinancieroAgentResponse`.
    """
    payload: OrquestadorAgentResponse = state["payload_orquestador"]

    contexto_especifico: str = next(
        (
            item.contexto_agente
            for item in payload.agentes_activados
            if item.agente == "financiero"
        ),
        state["pregunta_usuario"],
    )
    financiero = state["agentes"]["financiero"]

    res_financiero: FinancieroAgentResponse = financiero.consultar(contexto_especifico)
    return {"respuesta_financiero": res_financiero}


def nodo_bot(state: EstadoMultiAgente) -> Dict[str, Any]:
    """Ejecuta la lógica de negocio asociada al Agente General (Bot).

    Atiende consultas conversacionales generales o de soporte estándar cuando el
    orquestador enruta la solicitud al rol 'bot'.

    Args:
        state: Estado compartido del grafo.

    Returns:
        Dict[str, Any]: Diccionario con la clave `respuesta_bot` conteniendo
            la respuesta estructurada `BotAgentResponse`.
    """
    payload: OrquestadorAgentResponse = state["payload_orquestador"]

    contexto_especifico: str = next(
        (
            item.contexto_agente
            for item in payload.agentes_activados
            if item.agente == "bot"
        ),
        state["pregunta_usuario"],
    )
    bot = state["agentes"]["bot"]

    res_bot: BotAgentResponse = bot.consultar(contexto_especifico)
    return {"respuesta_bot": res_bot}


def nodo_sintetizador(state: EstadoMultiAgente) -> Dict[str, Any]:
    """Consolida las respuestas de múltiples subagentes en un único formato visual.

    Inspecciona las claves de respuesta presentes en el estado, formatea cada
    sección con sus respectivos encabezados y separadores Markdown, y genera la
    salida final unificada para el usuario.

    Args:
        state: Estado compartido que contiene las respuestas parciales de
            los subagentes ejecutados.

    Returns:
        Dict[str, Any]: Diccionario con la clave `respuesta_final` conteniendo
            el string unificado de la respuesta.
    """
    partes_respuesta: list[str] = []

    # Construcción modular de la respuesta evaluando la presencia de ejecuciones previas
    if state.get("respuesta_bot"):
        bot_res: BotAgentResponse = state["respuesta_bot"]
        partes_respuesta.append(f"🤖 **Asistente:** {bot_res.mensaje}")

    if state.get("respuesta_auditor"):
        auditor_res: AuditorAgentResponse = state["respuesta_auditor"]
        partes_respuesta.append(
            f"📋 **Dictamen Operativo/Auditoría:**\n{auditor_res.respuesta_directa}"
        )
        if auditor_res.responsable_operativo:
            partes_respuesta.append(
                f"_Responsable Operativo:_ {auditor_res.responsable_operativo}"
            )

    if state.get("respuesta_financiero"):
        fin_res: FinancieroAgentResponse = state["respuesta_financiero"]
        partes_respuesta.append(
            f"💰 **Cotización y Finanzas:**\n{fin_res.respuesta_cliente}"
        )

    # Unificación con separador estándar Markdown entre bloques de respuesta
    consolidado: str = "\n\n---\n\n".join(partes_respuesta)
    return {"respuesta_final": consolidado}