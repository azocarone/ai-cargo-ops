# Prompt's Desarrollo

---

# Rol
Redactor profesional en idioma español.

# Objetivo:
En el planteamiento conceptual normalizar los títulos de las características de los agentes de IA. Es decir, las características que sean similares en ambos agentes, deben llevar los mismos titulo con la finalidad de que exista una homogenización conceptual.

# Regla
No modificar el texto de los bloques markdown tipo JSON.

**Adjunto lo redactado**:

---

# Rol
Eres un experto desarrollador de Agentes de IA.

# Objetivo
Elaborar el prompt de sistema y salida estructurada JSON de un "Agente Financiero" de la empresa DEPORCA, encargada de operaciones de carga y logística marítima.

# Fuente de la Verdad
**Documentos adjuntos**:
- `tarifario_exportacion.pdf`
- `seccion_base_preguntas_respuestas.pdf`

# Reglas
- No inventes datos o informaciones.
- El `prompt de sistema` y `salida estructurada JSON (BaseModel)` deben diseñarse para que el nuevo agente responda consultas similares a los ejemplos contentivos en el documento adjunto: `seccion_base_preguntas_respuestas.pdf` en su sección `Consultas sobre Tarifas y Condiciones Comerciales (Clientes)`. 

---

Basado en el **documento adjunto**, analizar el **planteamiento del sistema** con la finalidad de verificar si los **prompts de sistemas** y las **salidas estructuradas** están correctamente planteados.

---

# ROL
Experto en redacción en idioma Español y desarrollador de Agentes de IA con Python.

# OBJETIVO
Inferir la conceptualización del "Agente Orquestador", basandote en el analisis del "Prompt de Sistema'" y la "Salida Estructurada Pydantic BaseModel".

# REGLAS
1. Los puntos a tratar en la conceptualización deben ser los siguientes:
- Contexto
- Mecanismos de operación
- Ejemplo de estructura de datos JSON 
2. La redacción debe ser del tipo "resumen ejecutivo", pero con un enfoque tecnico con la finalidad de que le sirva de documentación de apoyo de los requerimientos de la implementación del proyecto,

Adjunto prompt y estructura pydantic:

---

# Rol
Eres un experto desarrollador de Agentes de IA.

# Objetivo
Elaborar el prompt de sistema y salida estructurada JSON de un "Agente Bot" de la empresa DEPORCA, encargada de operaciones de carga y logística marítima.

# Reglas
- El `prompt de sistema` y `salida estructurada JSON (BaseModel)` deben diseñarse para el manejo de interacciones de cortesía (saludos/despedidas) y consultas fácticas, históricas o institucionales de DEPORCA.
- No debe aceptar ningún tipo de consulta adicional.