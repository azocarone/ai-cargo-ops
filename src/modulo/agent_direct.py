from typing import TypeVar, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from modulo.agent_base import AgenteBase

T = TypeVar('T')

class AgenteDirecto(AgenteBase[T]):
    """
    Subclase polimórfica para agentes que interactúan directamente con el LLM
    sin pasar por una etapa de recuperación de documentos (RAG).
    Ideal para Orquestadores, Clasificadores o Enrutadores.
    """

    def _crear_prompt_template(self, prompt_sistema: str) -> ChatPromptTemplate:
        """
        Sobrescribe el método de la clase base para eliminar la variable {contexto},
        ya que este agente no utiliza RAG.
        """
        return ChatPromptTemplate.from_messages([
            ("system", prompt_sistema),
            ("user", "{pregunta}")
        ])

    def _preparar_payload(self, pregunta_usuario: str) -> Dict[str, Any]:
        """
        Implementa la abstracción de la clase base.
        Prepara el diccionario conteniendo únicamente la pregunta del usuario.
        """
        self.logger.info("Preparando payload directo (sin consultar FAISS)")
        return {
            "pregunta": pregunta_usuario
        }