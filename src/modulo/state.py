"""Mapeo e inicialización del estado global para el grafo multi-agente.

Este módulo define la estructura de datos principal que fluye a través
del grafo de ejecución. Utiliza `TypedDict` para proveer un esquema
estricto con validación de tipos estática, facilitando el seguimiento
del ciclo de vida de los datos entre el orquestador y los subagentes.
"""

from typing import Any, Dict, Optional, TypedDict

from modulo.schemes import (
    AuditorAgentResponse,
    BotAgentResponse,
    FinancieroAgentResponse,
    OrquestadorAgentResponse,
)


class EstadoMultiAgente(TypedDict, total=False):
    """Representa el estado centralizado que transita entre los nodos del grafo.

    Este esquema almacena tanto los datos de entrada generados por el usuario
    como las inyecciones de dependencias necesarias para los agentes y las
    respuestas procesadas en cada nodo de la arquitectura.

    Attributes:
        pregunta_usuario: Consulta inicial o Prompt enviado por el usuario.
        agentes: Diccionario que actúa como contenedor de dependencias,
            mapeando nombres de agentes con sus instancias operativas.
        payload_orquestador: Estructura de salida estandarizada emitida por el
            agente orquestador para definir el enrutamiento o acción.
        respuesta_auditor: Resultado estructurado generado por el nodo
            de auditoría.
        respuesta_financiero: Resultado estructurado generado por el nodo
            financiero.
        respuesta_bot: Resultado estructurado del bot de respuesta general.
        respuesta_final: Síntesis consolidada destinada al usuario final.
    """

    pregunta_usuario: str
    agentes: Dict[str, Any]
    payload_orquestador: Optional[OrquestadorAgentResponse]
    respuesta_auditor: Optional[AuditorAgentResponse]
    respuesta_financiero: Optional[FinancieroAgentResponse]
    respuesta_bot: Optional[BotAgentResponse]
    respuesta_final: str