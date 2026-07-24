"""
state.py - Etapa 1: Mapeo del Estado Global del Grafo (State)
"""
from typing import Any, Dict, Optional, TypedDict

from modulo.schemes import (
    AuditorAgentResponse,
    BotAgentResponse,
    FinancieroAgentResponse,
    OrquestadorAgentResponse,
)


class EstadoMultiAgente(TypedDict):
    # Entrada inicial del usuario
    pregunta_usuario: str

    # Inyección dinámica de la fábrica de agentes
    agentes: Dict[str, Any]
    
    # Salida parseada del Orquestador
    payload_orquestador: Optional[OrquestadorAgentResponse]
    
    # Respuestas individuales de los subagentes (acumulativas mediante operator.add)
    respuesta_auditor: Optional[AuditorAgentResponse]
    respuesta_financiero: Optional[FinancieroAgentResponse]
    respuesta_bot: Optional[BotAgentResponse]
    
    # Consolidado final para presentar al usuario
    respuesta_final: str