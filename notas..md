## BLOQUE DE INSTANCIACIONES

```python
# Capa Superior: Orquestador (No requiere retriever ya que hereda de AgenteDirecto)
agent_orquestador = AgenteDirecto(
    prompt_sistema=PROMPT_ORQUESTADOR,
    esquema_respuesta=OrquestadorAgentResponse,
    nombre_agente="Orquestador",
    modo_desarrollo=modo_dev
)

# Capa Operativa: Auditor (Requiere retriever e inyecta la lógica RAG)
agent_auditor = AgenteRAG(
    retriever=retriever_compartido,
    prompt_sistema=PROMPT_AUDITOR,
    esquema_respuesta=AuditorAgentResponse,
    nombre_agente="Auditor",
    modo_desarrollo=modo_dev
)

# Capa Operativa: Financiero (Reutiliza el mismo retriever compartido)
agent_financiero = AgenteRAG(
    retriever=retriever_compartido,
    prompt_sistema=PROMPT_FINANCIERO,
    esquema_respuesta=FinancieroAgentResponse,
    nombre_agente="Financiero",
    modo_desarrollo=modo_dev
)

# Capa Operativa: Bot (No requiere retriever ya que hereda de AgenteDirecto)
agent_bot = AgenteDirecto(
    prompt_sistema=PROMPT_BOT,
    esquema_respuesta=BotAgentResponse,
    nombre_agente="Bot",
    modo_desarrollo=modo_dev
)
```

## ESQUEMAS JSON PYDANTIC BASEMODEL

```python
# =====================================================================
# ESQUEMAS DEL AGENTE ORQUESTADOR
# =====================================================================

class AgenteAsignado(BaseModel):
    agente: Literal["auditor", "financiero", "bot"] = Field(
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

# ---

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

# --- 

class AuditorAgentResponse(BaseModel):
    categoria_consulta: CategoriaConsulta = Field(
        ..., 
        description="Categoría general en la que se clasifica la consulta."
    )
    respuesta_directa: str = Field(
        ..., 
        description="Explicación detallada basándose ÚNICAMENTE en el contexto RAG."
    )
    responsable_operativo: str = Field(
        ..., 
        description="Cargo explícito mencionado en el texto que debe ejecutar o resolver la acción (ej. 'Agente de Aduanas', 'Supervisor de Almacén'). Colocar 'No especificado en manual' solo si no hay ningún cargo escrito."
    )
    fase_procedimiento: FaseProcedimiento = Field(
        ..., 
        description="Fase exacta del flujo operativo donde se ubica el tema."
    )
    sustento_legal_o_normativo: List[str] = Field(
        default_factory=list, 
        description="Leyes, providencias o secciones internas mencionadas en el contexto."
    )
    protocolo_emergencia: ProtocoloEmergencia = Field(
        ..., 
        description="Sub-objeto que detalla si la consulta es una contingencia/falla operativa física."
    )
    citas_evidencia: List[CitaBaseConocimiento] = Field(
        default_factory=list,
        description="Lista de fragmentos textuales del contexto RAG."
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

# =====================================================================
# ESQUEMAS DEL AGENTE BOT (Asistente Virtual)
# =====================================================================

class CategoriaIntencion(str, Enum):
    SALUDO = "saludo"
    DESPEDIDA = "despedida"
    INFORMACION_INSTITUCIONAL = "informacion_institucional"
    RESUMEN_SERVICIOS = "resumen_servicios"
    INFORMACION_CONTACTO = "informacion_contacto"
    FUERA_DE_AMBITO = "fuera_de_ambito"

class BotAgentResponse(BaseModel):
    esta_dentro_del_ambito: bool = Field(
        description="Indica si la consulta del usuario está dentro del ámbito permitido de DEPORCA."
    )
    categoria: CategoriaIntencion = Field(
        description="Categoría principal identificada en la interacción."
    )
    mensaje: str = Field(
        description="Respuesta textual amigable, profesional y estrictamente en español dirigida al usuario final."
    )
    redirigir_a_humano: bool = Field(
        default=False,
        description="Se activa en True si la consulta requiere atención comercial/operativa especializada fuera del bot.",
    )
    seguimiento_sugerido: Optional[str] = Field(
        default=None,
        description="Sugerencia breve opcional en español para guiar al usuario a otra consulta válida.",
    )
```

## EJEMPLOS DE COMO SE EMPLEAN LAS INSTANCIACIONES
```python
pregunta = "Hola, requiero exportar 3 contenedores en un mismo booking desde Valencia hacia el puerto. Además, uno de ellos tiene una factura con 5 ítems de clasificación arancelaria compleja. ¿Cuánto me costaría el agenciamiento, la DUA y el transporte? ¿Puedo pagar en bolívares?"

res_orquestador: OrquestadorAgentResponse = agent_orquestador.consultar(pregunta)
print(res_orquestador.model_dump_json(indent=4))

res_auditor: AuditorAgentResponse = agent_auditor.consultar(pregunta)
print(res_auditor.model_dump_json(indent=4))

res_financiero: FinancieroAgentResponse = agent_financiero.consultar(pregunta)
print(res_financiero.model_dump_json(indent=4))

res_bot: BotAgentResponse = agent_bot.consultar(pregunta)
print(res_bot.model_dump_json(indent=4))
```