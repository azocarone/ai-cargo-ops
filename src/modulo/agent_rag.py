"""Módulo para la definición del Agente RAG (Retrieval-Augmented Generation).

Proporciona una clase especializada que hereda de la clase base de agentes
para realizar búsquedas de contexto en bases de conocimiento vectoriales antes
de construir la carga útil (payload) enviada al modelo de lenguaje.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from langchain_core.documents import Document

from modulo.agent_base import AgenteBase

# Variable de tipo genérica utilizada para definir la estructura del esquema de respuesta.
T = TypeVar("T")


class AgenteRAG(AgenteBase[T]):
    """Agente de Inteligencia Artificial basado en Arquitectura RAG.

    Esta clase extiende la funcionalidad de `AgenteBase` incorporando una
    capa de recuperación de información (retriever). Permite inyectar contexto
    relevante extraído de fuentes de datos externas (p. ej., vector stores)
    dentro del flujo de generación de respuestas.

    Attributes:
        retriever: Componente encargado de realizar las búsquedas de
            similitud semántica e invocar documentos relevantes.
    """

    def __init__(
        self,
        retriever: Any,
        prompt_sistema: str,
        esquema_respuesta: Type[T],
        nombre_agente: Optional[str] = None,
        modo_desarrollo: bool = False,
    ) -> None:
        """Inicializa el agente RAG con su recuperador y configuración de LLM.

        Args:
            retriever: Instancia del recuperador de datos (p. ej., FAISS retriever).
            prompt_sistema: Instrucción base o rol asignado al modelo de lenguaje.
            esquema_respuesta: Clase/Modelo de datos (p. ej., Pydantic) para estructurar
                la salida esperada del modelo.
            nombre_agente: Identificador único o descriptivo del agente para trazabilidad/logs.
            modo_desarrollo: Activa banderas de depuración e inspección si es True.
        """
        self.retriever = retriever
        super().__init__(
            prompt_sistema=prompt_sistema,
            esquema_respuesta=esquema_respuesta,
            nombre_agente=nombre_agente,
            modo_desarrollo=modo_desarrollo,
        )

    def _formatear_documentos(self, documentos: List[Document]) -> str:
        """Sintetiza una lista de objetos Document en una cadena de texto estructurada.

        Extrae el contenido de cada fragmento y limpia la ruta de la fuente de origen
        para presentar un contexto claro y ordenado al modelo de lenguaje.

        Args:
            documentos: Colección de documentos recuperados desde el almacén vectorial.

        Returns:
            str: Bloque de texto con los fragmentos numerados y referenciados,
                o un mensaje predeterminado si la lista está vacía.
        """
        if not documentos:
            return "No se encontró información relevante."

        # Construcción eficiente del contexto mediante list comprehension y join
        # para evitar la reasignación continua de strings en memoria.
        fragmentos: List[str] = []
        for i, doc in enumerate(documentos, 1):
            fuente = doc.metadata.get("source", "Manual_Desconocido.pdf")
            # Extrae únicamente el nombre del archivo eliminando las rutas del sistema de archivos
            nombre_archivo = fuente.split("/")[-1].split("\\")[-1]
            fragmentos.append(
                f"--- Fragmento {i} (Origen: {nombre_archivo}) ---\n{doc.page_content}"
            )

        return "\n\n".join(fragmentos)

    def _preparar_payload(self, pregunta_usuario: str) -> Dict[str, Any]:
        """Prepara el diccionario de contexto e entrada requeridos por la plantilla de prompt.

        Sobrescribe la implementación de la clase base (Polimorfismo) para ejecutar
        la etapa de 'Retrieval' antes de ensamblar la entrada del modelo.

        Args:
            pregunta_usuario: Consulta realizada por el usuario en texto plano.

        Returns:
            Dict[str, Any]: Diccionario con las claves 'contexto' y 'pregunta'
                necesarias para la ejecución de la cadena o flujo de LangChain.
        """
        self.logger.info("Buscando evidencias en la base de conocimientos (Retriever)...")
        documentos_recuperados: List[Document] = self.retriever.invoke(pregunta_usuario)
        contexto_texto = self._formatear_documentos(documentos_recuperados)

        return {
            "contexto": contexto_texto,
            "pregunta": pregunta_usuario,
        }