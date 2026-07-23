"""
router.py - Etapa 3: Lógica de Enrutamiento Dinámico (Conditional Edges
"""
from typing import List
from modulo.state import EstadoMultiAgente

MAPA_NODOS = {
    "auditor": "nodo_auditor",
    "financiero": "nodo_financiero",
    "bot": "nodo_bot"
}

def ruteador_orquestador(state: EstadoMultiAgente) -> List[str]:
    """
    Analiza el payload del orquestador y devuelve la lista de nombres de nodos
    a los cuales debe dirigirse la ejecución de forma simultánea.
    """
    payload = state.get("payload_orquestador")

    if not payload or not payload.agentes_activados:
        return ["nodo_bot"]

    nodos_destino = [
        MAPA_NODOS[item.agente]
        for item in payload.agentes_activados
        if item.agente in MAPA_NODOS
    ]

    return nodos_destino if nodos_destino else ["nodo_bot"]