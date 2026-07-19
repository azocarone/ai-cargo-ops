# Modelos NVIDIA Build para RAG

Para un sistema RAG (*Retrieval-Augmented Generation*), el rendimiento no depende solo de que el modelo sea rápido, sino de **tres capacidades críticas**:

1. **Comprensión de contexto largo:** Que no se "pierda" ni invente cosas al leer los fragmentos de texto recuperados.
2. **Habilidad de Síntesis:** Que sepa extraer datos duros de tablas, PDFs o reportes sin distorsionar la información.
3. **Calidad del Embedder:** El modelo que convierte tus textos en vectores debe ser preciso, o de lo contrario recuperará información basura.

NVIDIA ha diseñado sus arquitecturas más recientes (especialmente la familia **Nemotron**) optimizándolas específicamente para tareas de RAG y pipelines empresariales.

---

## El Generador (El LLM que responde la pregunta)

Aquí es donde conectas tu base de conocimientos con la respuesta final.

### Para Producción (El Campeón del RAG)

* **`nvidia/llama-3.1-nemotron-51b-instruct`** o **`nvidia/llama-3.3-nemotron-super-49b-v1.5`**
> **Por qué:** NVIDIA tomó las bases de Llama y las entrenó específicamente para alineación en RAG, control de "alucinaciones" y síntesis de datos basados estrictamente en el contexto entregado. Es la recomendación oficial en los *RAG Blueprints* de NVIDIA.


* **`meta/llama-3.1-70b-instruct`**
> **Por qué:** Su enorme ventana de contexto te permite enviarle docenas de fragmentos recuperados de PDFs sin que pierda precisión (el famoso efecto de "perderse en el medio").

### Para Desarrollo (RAG Rápido y Económico)

* **`meta/llama-3.1-8b-instruct`**
> **Por qué:** Si estás probando la lógica de tu código en LangChain, indexando tus primeros archivos o estructurando los prompts del RAG, este modelo te dará respuestas inmediatas a coste cero de latencia.

---

## Los Embeddings (Para indexar y buscar en tus PDFs)

Si el modelo de embeddings es malo, tu RAG fallará aunque uses el LLM más inteligente del mundo. Para guardar tus textos en la base de datos vectorial (Chroma, Milvus, Pinecone, etc.), debes usar estos IDs exactos:

* **`nvidia/nv-embedqa-e5-v5`** *(Recomendado por defecto)*
> **Por qué:** Salido de la familia *NeMo Retriever*, está optimizado matemáticamente para queries de preguntas y respuestas (*QA*). Devuelve vectores de 1024 dimensiones que capturan con extrema precisión la semántica de documentos técnicos.


* **`nvidia/llama-3.2-nv-embedqa-1b-v2`**
> **Por qué:** Extremadamente ligero y veloz si vas a indexar millones de filas de texto en tiempo real en tu infraestructura local.

---

## Ejemplo Completo de un Pipeline RAG en LangChain

Así es como configuras ambos componentes en armonía utilizando los modelos óptimos para RAG:

```python
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Configurar el Embedder para transformar tus documentos y preguntas a vectores
embedder = NVIDIAEmbeddings(
    model="nvidia/nv-embedqa-e5-v5",
    nvidia_api_key="nvapi-..."
)

# 2. Configurar el LLM especializado de NVIDIA afinado para RAG y síntesis
llm = ChatNVIDIA(
    model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
    nvidia_api_key="nvapi-...",
    temperature=0.0  # Obligatorio en RAG: 0.0 evita que invente o alucine fuera del contexto
)

# 3. El Prompt típico de RAG (Asegurando que use el contexto)
prompt = ChatPromptTemplate.from_template("""
Eres un asistente experto. Responde la pregunta basándote ÚNICAMENTE en el contexto proporcionado. 
Si la respuesta no está en el contexto, di textualmente "No encontré esa información en los documentos".

Contexto:
{context}

Pregunta: {question}
Respuesta:""")

# Tu cadena de LangChain (Asumiendo que ya recuperaste tus fragmentos de la BD Vectorial)
rag_chain = prompt | llm | StrOutputParser()
```
