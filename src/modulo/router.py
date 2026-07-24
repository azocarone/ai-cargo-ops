"""Módulo de enrutamiento dinámico para arquitectura multi-agente.

Este módulo define la lógica de decisión (conditional edges) encargada de analizar
el estado global del flujo de trabajo y determinar qué nodos de procesamiento
deben activarse de manera paralela o condicional.

Uso típico:
    Este archivo se utiliza como función de enrutamiento condicional dentro de
    grafos de ejecución (p. ej., LangGraph), mapeando intenciones detectadas
    a nodos ejecutables.
"""

from typing import Dict, List, Final

from modulo.state import EstadoMultiAgente

# Configuración de Mapeo de Agentes a Nodos
# -----------------------------------------------------------------------------
# Un dict constante que traduce el identificador lógico del agente
# hacia el nombre explícito del nodo registrado en el grafo de ejecución.
MAPA_NODOS: Final[Dict[str, str]] = {
    "auditor": "nodo_auditor",
    "financiero": "nodo_financiero",
    "bot": "nodo_bot",
}

# Nodo por defecto al cual redirigir cuando no existe coincidencia o payload.
NODO_DEFAULT: Final[str] = "nodo_bot"


def ruteador_orquestador(state: EstadoMultiAgente) -> List[str]:
    """Determina los nodos destino a ejecutar analizando el estado global.

    Inspecciona el payload del orquestador dentro del estado de la ejecución.
    Si se detectan agentes activos válidos, traduce sus identificadores a
    nombres de nodos del grafo. En caso de ausencia de payload o incoincidencia,
    se aplica un mecanismo de tolerancia a fallos (fallback) redirigiendo al
    nodo por defecto.

    Args:
        state (EstadoMultiAgente): Estado actual del flujo de trabajo que
            contiene la información general y el `payload_orquestador`.

    Returns:
        List[str]: Lista con los nombres de los nodos de destino a los cuales
            debe fluir la ejecución (soporta ejecución en paralelo).
    """
    # Extracción del payload con manejo seguro (retorna None si no existe la clave)
    payload = state.get("payload_orquestador")

    # Guard Clause (Cláusula de Guarda):
    # Si no hay payload o no hay agentes activados en la lista, fallback directo.
    if not payload or not payload.agentes_activados:
        return [NODO_DEFAULT]

    # Comprensión de lista condicional para mapear agentes activados a nodos del grafo.
    # Se filtran únicamente los agentes que estén registrados en MAPA_NODOS para evitar KeyError.
    nodos_destino: List[str] = [
        MAPA_NODOS[item.agente]
        for item in payload.agentes_activados
        if item.agente in MAPA_NODOS
    ]

    # Retorno condicional: si ninguno de los agentes enviados coincidió con el mapeo,
    # se garantiza la continuidad del flujo enviándolo al nodo por defecto.
    return nodos_destino if nodos_destino else [NODO_DEFAULT]