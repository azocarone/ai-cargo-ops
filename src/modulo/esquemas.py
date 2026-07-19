"""
JSON's Estructurados - Modelos Pydantic (BaseModel)
"""

from enum import Enum
from typing import List, Literal, Optional
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

# =====================================================================
# ESQUEMAS DEL AGENTE AUDITOR
# =====================================================================

# --- Enums para restringir las clasificaciones del agente ---

class CategoriaConsulta(str, Enum):
    PRE_EMBARQUE = "Procedimientos de Pre-Embarque"
    OPERACION_ADUANERA = "Operación Aduanera"
    POST_EMBARQUE = "Post-Embarque"
    CONTROL_INTERNO = "Control Interno y Archivo"
    PROTOCOLOS_EMERGENCIA = "Protocolo de Incidentes y Emergencias"
    ESCALAR = "No Detectado / Escalar"

class FaseProcedimiento(str, Enum):
    PRE_EMBARQUE = "Fase de Pre-Embarque (Procedimiento A)"
    OPERACION_ADUANERA = "Fase de Operación Aduanera (Procedimiento B)"
    POST_EMBARQUE = "Fase de Post-Embarque (Procedimiento C)"
    CONTROL_INTERNO = "Normas Generales de Control Interno"
    NO_APLICA = "No Aplica"

class ProtocoloEmergencia(BaseModel):
    aplica_incidente: bool = Field(
        ..., 
        description="Indica si la consulta describe un escenario de falla, alerta o contingencia en puerto o planta."
    )
    acciones_inmediatas: Optional[List[str]] = Field(
        default=None,
        description="Pasos de emergencia ordenados cronológicamente leídos en el manual para contener el incidente."
    )
    documentos_requeridos: Optional[List[str]] = Field(
        default=None,
        description="Documentación obligatoria indicada en el manual a consignar ante las autoridades por el incidente."
    )

# --- Citas del RAG ---

class CitaBaseConocimiento(BaseModel):
    archivo_origen: str = Field(
        ..., 
        description="Nombre del archivo PDF de donde se extrajo la información (ej. Manual_Exportacion.pdf)."
    )
    texto_exacto: str = Field(
        ..., 
        description="Frase o fragmento textual idéntico tomado del contexto RAG que justifica la respuesta."
    )

# --- Modelos Adaptados ---

class AuditorAgentResponse(BaseModel):
    categoria_consulta: CategoriaConsulta = Field(
        ..., 
        description="Categoría general en la que se clasifica la consulta del usuario."
    )
    respuesta_directa: str = Field(
        ..., 
        description="Explicación detallada y profesional que responde a la pregunta basándose ÚNICAMENTE en el contexto proporcionado."
    )
    responsable_operativo: str = Field(
        ..., 
        description="Cargo encargado de la tarea. Si no se menciona explícitamente en el texto, colocar 'No especificado en manual'."
    )
    fase_procedimiento: FaseProcedimiento = Field(
        ..., 
        description="Fase exacta del flujo operativo de exportación donde se ubica el tema consultado."
    )
    sustento_legal_o_normativo: List[str] = Field(
        ..., 
        description="Leyes, providencias o secciones internas del manual mencionadas explícitamente en los textos recuperados."
    )
    protocolo_emergencia: ProtocoloEmergencia = Field(
        ..., 
        description="Sub-objeto que detalla el protocolo a seguir en caso de incidentes."
    )
    citas_evidencia: List[CitaBaseConocimiento] = Field(
        ...,
        description="Lista de fragmentos textuales del contexto RAG que demuestran la veracidad de los datos entregados."
    )

# =====================================================================
# ESQUEMAS DEL AGENTE FINANCIERO
# =====================================================================

class ConceptoDetalle(BaseModel):
    concepto: str = Field(description="Nombre o descripción detallada del servicio o cargo aplicado.")
    tarifa_base_usd: float = Field(description="Monto base cobrado por el concepto en USD. 0.0 si no aplica.")
    unidad_cobro: str = Field(description="Unidad de medida del cobro (ej. Por Contenedor, Por Evento, Por Hora, Por Documento, N/A).")
    observaciones: str = Field(description="Notas adicionales, excepciones o base legal interna del cobro.")

class FinancieroAgentResponse(BaseModel):
    analisis_consulta: str = Field(description="Breve razonamiento lógico y financiero basado estrictamente en el tarifario.")
    respuesta_cliente: str = Field(description="Respuesta directa, empática y clara redactada para el cliente.")
    desglose_costos: List[ConceptoDetalle] = Field(default=[], description="Lista de los conceptos y tarifas asociados a la consulta.")
    politica_aplicable: Optional[str] = Field(None, description="Especificación de políticas de facturación (Anticipos, Demurrage, Pago en Bs/BCV, Almacenaje) si aplica.")
    monto_total_estimado_usd: float = Field(description="Suma total de los cargos identificados en USD. 0.0 si es informativo.")





