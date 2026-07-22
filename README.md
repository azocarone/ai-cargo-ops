# 🤖 Agente de IA para Consultas de Operaciones y Logística Marítima

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub: Profile](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/azocarone)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![NVIDIA Build](https://img.shields.io/badge/NVIDIA%20Build-76B900?style=flat&logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![RAG](https://img.shields.io/badge/RAG-Retrieval%20Augmented%20Generation-8A2BE2?style=flat)](https://es.wikipedia.org/wiki/Generaci%C3%B3n_aumentada_por_recuperaci%C3%B3n)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-004A7C?style=flat&logo=python&logoColor=white)](https://pymupdf.readthedocs.io/)
[![FAISS CPU](https://img.shields.io/badge/FAISS%20CPU-005A9C?style=flat&logo=meta&logoColor=white)](https://github.com/facebookresearch/faiss)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)

Agente diseñado mediante el procesamiento del lenguaje natural para optimizar y resolver consultas sobre las operaciones de carga y logística marítima de la empresa, "_Almacenes y Depósitos Integrales Portuarios, C.A._" (**_DEPORCA_**):

<div align="center">
  <img src="./assets/img/guia_exportacion_puerto.png" alt="Guía de exportación en puerto" width="95%" height="95%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
</div>

<div align="right">
  <p><br>🔗 <a href="#">Explorar Deploy</a></p>
</div>

---

## 📖 Tabla de Contenidos

- ⚑ [Planteamiento del Sistema](./docs/planteamiento_del_sistema.md)
- ⚑ [Actividades del Desarrollo](#-actividades-del-desarrollo)

---

## Planteamiento del Sistema (Resumen)

El desarrollo de un **sistema multi-agente** plantea la optimización de las consultas operativas y logísticas de la empresa portuaria **DEPORCA**. La arquitectura se basa en un **Agente Orquestador** que clasifica y redirige las solicitudes hacia tres especialistas: el **Agente Auditor**, el **Agente Financiero** y el **Agente Bot**. Cada uno opera bajo un esquema de **"fuente de verdad"**, utilizando manuales de normas y tarifarios oficiales para garantizar respuestas precisas y sin errores. Este enfoque permite segmentar tareas complejas, como la gestión de **incidentes de seguridad** o el cálculo de **costos de exportación**, asegurando la trazabilidad legal en cada interacción. Al separar las responsabilidades, el sistema mejora la **eficiencia operativa** y reduce significativamente el riesgo de proporcionar información incorrecta al usuario.

<div align="right">
  <p>🔗 <a href="./docs/planteamiento_del_sistema.md">Para ver más ...</a></p>
</div>

---

## ⚑ Actividades del Desarrollo

1. **Inicialización**: La fase inicial comprende la creación del repositorio en **GitHub**, la asignación de la licencia (**MIT**) para la gestión de los términos de uso del código y la configuración del entorno virtual de **Python**.

2. **Configuración del Motor (LLM)**: Tras la preparación de los datos, se procede a la configuración del modelo de lenguaje. Esto incluye la conexión a la API de **NVIDIA Build**, la gestión y prueba de tokens, la selección del modelo pertinente y la verificación de su correcto funcionamiento.

3. **Preparación de los Datos Base**: Previo a la integración de inteligencia artificial, se requiere el procesamiento de la información. En esta etapa se implementan scripts con **PyMuPDF** para la extracción de texto desde manuales.

4. **Desarrollo de la Lógica (Cadenas base)**: Mediante el uso de **LangChain**, se diseñan los *prompts*, se configura la memoria a corto plazo y se generan los *embeddings* (vectorización de archivos PDF). Asimismo, se implementa la arquitectura **RAG** para habilitar la recuperación de información desde documentos locales, garantizando que el modelo base sus respuestas en los datos provistos.

5. **Implementación del Agente (Flujos con Estado)**: La etapa final integra el sistema RAG construido en el paso anterior con **LangGraph** para establecer un sistema autónomo. Se diseña un flujo de trabajo cíclico que permite al agente evaluar la precisión de las respuestas obtenidas, determinar la necesidad de utilizar herramientas adicionales o ejecutar nuevas iteraciones de búsqueda en la base documental.

---

## 🗺 Roadmap

- [x]
- [ ]

---

## ⚖️ Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. El contenido personal y la trayectoria profesional son propiedad intelectual de **José Azócar**.

---

<div align="right">
    <strong>José Antonio Azócar Marcano</strong><br>
    Ing. Informático | Consultor I&O: Infraestructura y Ops.<br>
    <a href="https://github.com/azocarone">@azocarone</a>
</div>
