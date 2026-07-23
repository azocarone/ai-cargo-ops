"""
builder.py - Etapa 4: Ensamblado e Construcción del Grafo (StateGraph)
"""
from langgraph.graph import StateGraph, START, END
from state import EstadoMultiAgente
from nodes import (
    nodo_orquestador,
    nodo_auditor,
    nodo_financiero,
    nodo_bot,
    nodo_sintetizador
)
from router import ruteador_orquestador

def crear_grafo_deporca():
    """Construye y compila el flujo de LangGraph para DEPORCA."""
    
    # 1. Instanciar el StateGraph
    builder = StateGraph(EstadoMultiAgente)

    # 2. Registrar Nodos
    builder.add_node("nodo_orquestador", nodo_orquestador)
    builder.add_node("nodo_auditor", nodo_auditor)
    builder.add_node("nodo_financiero", nodo_financiero)
    builder.add_node("nodo_bot", nodo_bot)
    builder.add_node("nodo_sintetizador", nodo_sintetizador)

    # 3. Punto de entrada inicial
    builder.add_edge(START, "nodo_orquestador")

    # 4. Enrutamiento Condicional (Fan-out)
    builder.add_conditional_edges(
        "nodo_orquestador",
        ruteador_orquestador,
        {
            "nodo_auditor": "nodo_auditor",
            "nodo_financiero": "nodo_financiero",
            "nodo_bot": "nodo_bot"
        }
    )

    # 5. Reconvergencia (Fan-in) hacia el sintetizador
    builder.add_edge("nodo_auditor", "nodo_sintetizador")
    builder.add_edge("nodo_financiero", "nodo_sintetizador")
    builder.add_edge("nodo_bot", "nodo_sintetizador")

    # 6. Finalización
    builder.add_edge("nodo_sintetizador", END)

    # 7. Compilar
    return builder.compile()