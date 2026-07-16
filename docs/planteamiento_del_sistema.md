## Planteamiento del Sistema

<div align="center">
  <img src="../assets/img/sistema_multi_agente_exportacion_especializada.png" alt="Sistena Multi-Agente DEPORCA: Inteligencia Especializada en Exportación" width="95%" height="95%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
</div>

---

El enfoque radica en el desarrollo de un sistema de **multi-agentes**, ya que permitirá una especialización profunda basada en la documentación de **DEPORCA**:

- [Manual de Normas y Procedimientos de Exportación](../assets/manual_normas_procedimientos_exportacion.pdf)
- [Tarifario de Exportación](../assets/tarifario_exportacion.pdf)
- [Sección Base de Preguntas y Respuestas](../assets/seccion_base_preguntas_respuestas.pdf)

---

En un ecosistema multi-agente para las "Consultas de Operaciones y Logística Marítima de **DEPORCA**", la estructura funcionará bajo una jerarquía coordinada:

### 1. Agente Orquestador (Orquestador de Casos y Enrutamiento Paralelo)

- **Contexto**: Cerebro de distribución y primera línea automatizada del sistema. Su función es estrictamente analítica: descompone el mensaje del usuario, identifica todas las intenciones implícitas y delega las tareas a los canales adecuados de forma simultánea. Tiene prohibido interactuar conversacionalmente o responder dudas con el cliente.

- **Mecanismo de Operación / Verdad**:

    - **Segmentación Multitarea**: Si un mensaje contiene múltiples solicitudes (por ejemplo, el costo de un flete y una duda sobre el precinto), el Orquestador no elige una sola; divide la consulta y activa en paralelo o secuencia los nombres de las entidades correspondientes (`auditor`, `financiero`, `documental`).

    - **Filtro de Contención (`bot`)**: Si la entrada carece de contexto identificable, es un saludo o no requiere un especialista, activa la bandera `bot` para desviar la atención a un flujo conversacional automatizado de recolección de datos.

    - **Gestión de Prioridades**: Clasifica el caso dentro de una escala operativa (`baja`, `mediana`, `alta`) para determinar el orden de atención en las colas de trabajo.

    - **Auditoría de Datos (`datos_faltantes`)**: Detecta la ausencia de datos operativos críticos (Booking, contenedor, etc.) para que el especialista reciba el caso sabiendo exactamente qué información inicial falta solicitar.

- **Salida y Formato**: Retorna exclusivamente un objeto JSON estructurado que define los agentes que se deben activar, el nivel de prioridad de la consulta y la lista de campos o datos faltantes requeridos para iniciar la operación.

- **Ejemplo Operativo**:

    - **Mensaje del usuario**: "¿Cuánto me sale el flete para mañana? Y otra cosa, ¿cómo hago con la inspección del precinto?".

    - **Salida**:

        ```json
        {
            "agentes_activados": ["financiero", "auditor"],
            "prioridad": "mediana",
            "datos_faltantes": ["booking", "tipo_carga"]
        }
        ```
---

### 2. Colaboración de Especialistas (Multi-Agentes)

Para conformar un sistema multi-agente robusto para **DEPORCA**, se deben definir roles especializados que utilicen las fuentes documentales como su única base de conocimiento. Al separar las responsabilidades, se garantiza que cada agente use solo la "**fuente de verdad**" necesaria, reduciendo los tokens y alucinaciones. A continuación se detalla la configuración para cada agente, integrando el **Manual de Normas**, el **Tarifario** y la **Matriz de Control**:

#### Agente Auditor (Basado en el Manual)

- **Contexto**: Especialista técnico-legal encargado de auditar y verificar el cumplimiento normativo en las tres fases de exportación (Pre-Embarque, Operación Aduanera y Post-Embarque) en la jurisdicción de la Aduana Principal de Puerto Cabello.

- **Mecanismo de Operación / Verdad**: Restringido estrictamente al Manual de Exportación y sección de consultas de DEPORCA, con deslinde de responsabilidades operativas e inhabilitación para responder ante la falta de datos explícitos.

- **Salida y Formato**: Retorna exclusivamente un objeto JSON estructurado (BaseModel de Pydantic) libre de texto complementario. Este objeto clasifica la consulta, define al responsable operativo de la tarea, provee el sustento normativo/legal (LOPA, COT, LOD, etc.) y encapsula un sub-objeto dinámico para la contención de riesgos que detalla acciones inmediatas y documentos requeridos ante alertas o contingencias en puerto.

- **Ejemplo Operativo**:

    - **Mensaje del usuario**: "¿Qué documentos integran el "Expediente Especial de Trazabilidad de Planta" en caso de una alerta antidrogas?".

    - **Salida**:

        ```json
        {
            "categoria_consulta": "Protocolo de Incidentes y Emergencias",
            "respuesta_directa": "En caso de presentarse una alerta antidrogas (marcaje de can o irregularidades de densidad), se debe consignar de forma obligatoria el Expediente Especial de Trazabilidad de Planta para blindar jurídicamente a la empresa y demostrar que la cadena logística de origen no fue vulnerada.",
            "responsable_operativo": "Agente de Aduanas y Representante Legal (con soporte del Supervisor de Almacén)",
            "fase_procedimiento": "Fase de Operación Aduanera (Procedimiento B)",
            "sustento_legal_o_normativo": [
                "Ley Orgánica de Drogas (LOD)",
                "Caso 6.2 del Protocolo para el Manejo de Incidentes"
            ],
            "protocolo_emergencia": {
                "aplica_incidente": true,
                "acciones_inmediatas": [
                    "Exigir estar presentes de manera física e ininterrumpida en el Acto de Vaciado de Emergencia (Unstuffing).",
                    "Consignar de forma inmediata el Expediente Especial de Trazabilidad ante las autoridades competentes (GNB/Dirección Antidrogas)."
                ],
                "documentos_requeridos": [
                    "Copia del registro de la ruta satelital (GPS) del transporte desde la salida de la empresa hasta el puerto.",
                    "Reporte fotográfico con marca de agua (fecha y hora) del momento exacto del cierre de las compuertas en planta.",
                    "Bitácora de firmas del personal de seguridad interna que custodió el llenado."
                ]
            }
        }
        ```

---

### Ventajas del Enfoque Multi-Agente para DEPORCA

1. **Contexto Limpio:** El Agente Financiero no necesita "leer" el protocolo de incidentes antidrogas para cotizar un flete, lo que hace sus respuestas más rápidas y precisas.

2. **Seguridad Operativa:** Como indica el manual, "cualquier manifestación verbal carece de validez legal". Un sistema multi-agente permite que la respuesta final sea validada por el **Agente Auditor** antes de mostrarse al usuario, asegurando que se cite siempre la base legal correcta (LOA, COT o LOD).

3. **Flujos de Trabajo Complejos:** Permite resolver situaciones mixtas. Por ejemplo, ante una "Discrepancia de Peso" (Caso 6.1), el **Agente Auditor** dicta el protocolo de re-pesaje, mientras el **Agente Financiero** calcula automáticamente el costo de la "Enmienda de DUA" ($100 USD) según el tarifario.

---

###  
### EN DESARROLLO
###

- **Agente Financiero (Basado en el Tarifario):** Se especializa en la rentabilidad, el cobro de servicios, cálculos exactos, basándose en el Tarifario de Exportación, aplicación de la tasa cambiaría del Banco Central de Venezuela (**BCV**) y verificación de que se cumpla la política de "Anticipo Obligatorio". Su salida será una **cotización estructurada**.

- **Agente Documental (Basado en la Matriz de Control):** Su única función es validar que el expediente cumpla con la lista de documentos obligatorios (Factura, Packing List, DUA, etc.) antes de autorizar el ingreso a la zona primaria portuaria.

---

###
### Roles Especializados de los Agentes
###  
### EN DESARROLLO
###

---

#### Agente Financiero

- **Prompt de Sistema:**

```text
Eres el Analista Financiero y de Facturación de DEPORCA. Tu función es procesar cálculos de costos logísticos y asegurar el cumplimiento de las políticas de cobro de la organización.

Analiza el mensaje y devuelve únicamente un objeto JSON que respete estrictamente la siguiente estructura:

{
    "items_cotizados": [
        {"servicio": "Nombre del concepto", "costo": 0.0}
    ],
    "monto_total_usd": 0.0,
    "requiere_anticipo": true,
    "observacion_cambiaria": "Nota sobre el uso estricto de la tasa oficial BCV"
}

Reglas:
1. Tarificación Base: Aplicar estrictamente $350.00 USD por el primer contenedor y $150.00 USD por cada adicional bajo el mismo booking.
2. Recargos por Complejidad: Facturar $25.00 USD por cada ítem adicional a partir de la tercera subpartida arancelaria.
3. Política de Anticipos: Prohibir explícitamente cualquier financiamiento de tasas de Bolipuertos o impuestos del SENIAT; el cliente debe transferir el 100% de los fondos de manera anticipada.
4. Conversión Cambiaria: Todo pago en bolívares debe calcularse exclusivamente utilizando la tasa oficial del Banco Central de Venezuela (BCV) vigente al momento.
```

- **Estructura de Salida (JSON):**

```python
class FinancieroOut(BaseModel):
    # Desglose de conceptos según el tarifario
    items_cotizados: List[dict] # Ej: [{"servicio": "Agenciamiento", "costo": 350.00}]
    # Sumatoria total en divisas
    monto_total_usd: float
    # Recordatorio de la política de anticipos del 100%
    requiere_anticipo: bool
    # Nota sobre el uso de la tasa BCV vigente
    observacion_cambiaria: str
```

#### Agente Documental

- **Prompt de Sistema:**

```text
Eres el Analista de Documentación y Permisología de DEPORCA. Tu responsabilidad es auditar la integridad del expediente aduanero (físico y digital) para garantizar que la carga sea apta para la transmisión de la DUA y el ingreso a la zona primaria portuaria de Puerto Cabello.

Analiza el mensaje y devuelve únicamente un objeto JSON que respete estrictamente la siguiente estructura:

{
    "estatus_expediente": "Apto para Transmisión | Incompleto | En Revisión",
    "documentos_pendientes": ["Lista de documentos faltantes según la matriz"],
    "alerta_permisologia": "Observaciones sobre vigencia de certificados"
}

Reglas:
1. Fuente de Verdad: Tu único criterio de validación es la Matriz de Control Documental del manual.
2. Validación de Obligatoriedad: Debes verificar la presencia de los 5 documentos críticos: Factura Comercial, Lista de Empaque (Packing List), Declaración Única de Aduanas (DUA), Conocimiento de Embarque (B/L) y el Acta de Inspección Antidrogas.
3. Gestión de Condicionales: Para productos específicos, debes exigir los Certificados de Origen y los permisos Fitosanitarios/Sanitarios del INSAI o Ministerio de Salud.
4. Alerta de Vigencia: Si detectas retrasos logísticos, debes advertir sobre el riesgo de vencimiento extemporáneo de permisos y sugerir el protocolo de "Fuerza Mayor" amparado en la LOPA.
```

- **Estructura de Salida (JSON):**

```python
class DocumentacionOut(BaseModel):
    # Determina si el expediente puede ser transmitido al SIDUNEA
    estatus_expediente: Literal["Apto para Transmisión", "Incompleto", "En Revisión"]
    # Lista de documentos que faltan según la Matriz de Control
    documentos_pendientes: List[str]
    # Alerta sobre vencimiento de permisos (Ej: Fitosanitarios)
    alerta_permisologia: str
```