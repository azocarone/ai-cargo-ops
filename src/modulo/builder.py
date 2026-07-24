"""Módulo de construcción e interconexión del grafo multi-agente (StateGraph).

Este módulo define la topología de ejecución para el sistema multi-agente de
DEPORCA utilizando LangGraph. Configura el flujo de trabajo desde el punto de
entrada inicial, la orquestación y enrutamiento dinámico (fan-out), hasta la
reconvergencia en el sintetizador (fan-in) y la finalización.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from modulo.nodes import (
    nodo_auditor,
    nodo_bot,
    nodo_financiero,
    nodo_orquestador,
    nodo_sintetizador,
)
from modulo.router import ruteador_orquestador
from modulo.state import EstadoMultiAgente


def crear_grafo_deporca() -> CompiledStateGraph:
    """Construye, interconecta y compila el flujo de trabajo de LangGraph.

    Establece la arquitectura del grafo multi-agente para DEPORCA siguiendo un
    patrón de Orquestación-Reconvergencia:
    
    1. **Entrada:** `START` redirige la consulta inicial al `nodo_orquestador`.
    2. **Orquestación (Fan-out):** El `ruteador_orquestador` evalúa el estado
       y decide hacia qué sub-agente especializado delegar la tarea.
    3. **Reconvergencia (Fan-in):** Todos los sub-agentes convergen sus
       respuestas intermedias hacia el `nodo_sintetizador`.
    4. **Salida:** El sintetizador procesa la respuesta final y concluye en `END`.

    Returns:
        CompiledStateGraph: Instancia ejecutable del grafo compilado lista para
            invocarse mediante `.invoke()` o `.stream()`.
    """
    # Inicialización del grafo delimitado por la estructura de EstadoMultiAgente
    builder = StateGraph(EstadoMultiAgente)

    # Registro de unidades de procesamiento (nodos de agentes y funciones)
    builder.add_node("nodo_orquestador", nodo_orquestador)
    builder.add_node("nodo_auditor", nodo_auditor)
    builder.add_node("nodo_financiero", nodo_financiero)
    builder.add_node("nodo_bot", nodo_bot)
    builder.add_node("nodo_sintetizador", nodo_sintetizador)

    # Conexión del punto de entrada hacia la etapa de orquestación inicial
    builder.add_edge(START, "nodo_orquestador")

    # Enrutamiento condicional (Fan-out):
    # La función 'ruteador_orquestador' decide dinámicamente qué rama ejecutar.
    # El diccionario actúa como mapa explícito de rutas permitidas.
    builder.add_conditional_edges(
        "nodo_orquestador",
        ruteador_orquestador,
        {
            "nodo_auditor": "nodo_auditor",
            "nodo_financiero": "nodo_financiero",
            "nodo_bot": "nodo_bot",
        },
    )

    # Reconvergencia de flujos (Fan-in):
    # Independientemente de la rama ejecutada, la salida se centraliza en el sintetizador.
    builder.add_edge("nodo_auditor", "nodo_sintetizador")
    builder.add_edge("nodo_financiero", "nodo_sintetizador")
    builder.add_edge("nodo_bot", "nodo_sintetizador")

    # Cierre del ciclo de vida del grafo
    builder.add_edge("nodo_sintetizador", END)

    # Compilación del estado en un objeto ejecutable por el motor de LangGraph
    return builder.compile()