"""Módulo que define la implementación concreta de un agente de interacción directa.

Proporciona la clase `AgenteDirecto`, especializada en procesar solicitudes que
no requieren mecanismos de recuperación de información externa (RAG), tales como
orquestadores, clasificadores de intenciones o enrutadores de flujos.
"""

from typing import Any, Dict, TypeVar

from langchain_core.prompts import ChatPromptTemplate

from modulo.agent_base import AgenteBase

# Variable de tipo genérico para especificar el tipo de salida estructurada
# esperado por la clase base AgenteBase (e.g., modelos Pydantic o tipos primitivos).
T = TypeVar("T")


class AgenteDirecto(AgenteBase[T]):
    """Agente de interacción directa con el modelo de lenguaje (sin RAG).

    Subclase concreta de `AgenteBase` diseñada para escenarios donde la
    respuesta se genera a partir de las instrucciones del sistema y la consulta
    del usuario, eliminando el overhead de búsqueda en bases de datos vectoriales.

    Type Parameters:
        T: El tipo de dato estructurado esperado como respuesta del agente.
    """

    def _crear_prompt_template(self, prompt_sistema: str) -> ChatPromptTemplate:
        """Crea la plantilla de prompt omitiendo variables de contexto externo.

        Sobrescribe el método protegido de la clase base (`Template Method`)
        para construir un pipeline simplificado compuesto únicamente por el rol
        de sistema y la entrada directa del usuario.

        Args:
            prompt_sistema: Instrucciones y directivas para el comportamiento
                del modelo de lenguaje.

        Returns:
            ChatPromptTemplate: Plantilla estructurada lista para ser invocada por LangChain.
        """
        # Se omite intencionalmente la variable {contexto} usada en pipelines RAG
        return ChatPromptTemplate.from_messages([
            ("system", prompt_sistema),
            ("user", "{pregunta}"),
        ])

    def _preparar_payload(self, pregunta_usuario: str) -> Dict[str, Any]:
        """Empaqueta la pregunta del usuario en el diccionario de entrada para el prompt.

        Satisface el método abstracto de `AgenteBase` aislando los datos de entrada
        requeridos por la plantilla configurada en `_crear_prompt_template`.

        Args:
            pregunta_usuario: Texto o consulta ingresada por el usuario.

        Returns:
            Dict[str, Any]: Mapeo de variables esperadas por el prompt
            (clave: 'pregunta').
        """
        # Traza de auditoría: Confirma la omisión consciente de la búsqueda en índices vectoriales
        self.logger.info("Preparando payload directo (sin consultar FAISS/RAG)")

        return {
            "pregunta": pregunta_usuario,
        }