from typing import List, Literal
from pydantic import BaseModel, Field

# =====================================================================
# ESQUEMAS DEL AGENTE ORQUESTADOR
# =====================================================================

class AgenteAsignado(BaseModel):
    agente: Literal["auditor", "financiero", "documental", "bot"] = Field(
        ...,
        description="Identificador del agente especializado o bot que debe activarse."
    )
    contexto_agente: str = Field(
        ...,
        description=(
            "Fragmento exacto del texto del usuario (o síntesis fiel del requerimiento específico) "
            "que este agente necesita para resolver su tarea. Si es 'bot', incluye el mensaje completo."
        )
    )

class OrquestadorAgentResponse(BaseModel):
    agentes_activados: List[AgenteAsignado] = Field(
        ..., 
        description="Lista de objetos que detallan qué agentes se activan y qué fragmento de la consulta les corresponde."
    )
    prioridad: Literal["baja", "mediana", "alta"] = Field(
        ..., 
        description="Nivel de prioridad determinado para la atención y resolución del caso."
    )
    datos_faltantes: List[str] = Field(
        ..., 
        description="Datos críticos que no se proporcionaron. Vacío [] si todo está completo o es un saludo."
    )