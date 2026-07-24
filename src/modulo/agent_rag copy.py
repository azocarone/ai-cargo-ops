from typing import List, Type, TypeVar
from langchain_core.documents import Document
from modulo.agent_base import AgenteBase

T = TypeVar('T')

class AgenteRAG(AgenteBase[T]):
    def __init__(self, retriever, prompt_sistema: str, esquema_respuesta: Type[T], nombre_agente: str = None, modo_desarrollo: bool = False):
        self.retriever = retriever
        # Llamamos al constructor de la base
        super().__init__(prompt_sistema, esquema_respuesta, nombre_agente, modo_desarrollo)

    def _formatear_documentos(self, documentos: List[Document]) -> str:
        if not documentos:
            return "No se encontró información relevante."
        texto_formateado = ""
        for i, doc in enumerate(documentos, 1):
            fuente = doc.metadata.get("source", "Manual_Desconocido.pdf")
            nombre_archivo = fuente.split("/")[-1]
            texto_formateado += f"--- Fragmento {i} (Origen: {nombre_archivo}) ---\n{doc.page_content}\n\n"
        return texto_formateado

    # Sobrescribimos el método aplicando POLIMORFISMO
    def _preparar_payload(self, pregunta_usuario: str) -> dict:
        self.logger.info("Buscando evidencias en los manuales (FAISS)...")
        documentos_recuperados = self.retriever.invoke(pregunta_usuario)
        contexto_texto = self._formatear_documentos(documentos_recuperados)
        
        return {
            "contexto": contexto_texto,
            "pregunta": pregunta_usuario
        }