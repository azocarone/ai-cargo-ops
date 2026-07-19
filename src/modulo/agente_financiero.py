import logging
from modulo.gestor_llm import GestorLLM
from modulo.esquemas import FinancieroAgentResponse
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from modulo.prompts import PROMPT_FINANCIERO

logger = logging.getLogger(__name__)

class AgenteFinanciero:
    def __init__(self, retriever, modo_desarrollo: bool=False):
        """
        Inicializa el agente uniendo el buscador de documentos (retriever)
        y la configuración del motor del LLM.
        """

        self.retriever = retriever
        
        logger.info("Inicializando el motor de IA")
        llm = GestorLLM(modo_desarrollo=modo_desarrollo)
        llm_base = llm.obtener_llm()
        
        # Convierte el LLM base en un LLM Estructurado usando el modelo Pydantic
        # Esto le quita la capacidad de 'chatear' libremente y lo obliga a rellenar el JSON
        self.llm_estructurado = llm_base.with_structured_output(FinancieroAgentResponse)
        
        # Diseño del molde del mensaje (Prompt Template) para LangChain
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", PROMPT_FINANCIERO),
            ("user", "CONTEXTO DE REFERENCIA:\n{contexto}\n\nPREGUNTA USUARIO: {pregunta}")
        ])
        
        # Construcción de la cadena ejecutable (Chain)
        self.cadena = self.prompt_template | self.llm_estructurado

    def _formatear_documentos(self, documentos: List[Document]) -> str:
        """
        Toma los fragmentos (chunks) encontrados por FAISS y los une en 
        un solo texto limpio, incluyendo el nombre del archivo de origen.
        """
        if not documentos:
            return "No se encontró información relevante en los manuales para esta consulta."
            
        texto_formateado = ""
        for i, doc in enumerate(documentos, 1):
            # Extracción del nombre del PDF desde los metadatos generados por PyMuPDFLoader
            fuente = doc.metadata.get("source", "Manual_Desconocido.pdf")
            nombre_archivo = fuente.split("/")[-1] # Limpiar la ruta para solo dejar el nombre
            
            texto_formateado += f"--- Fragmento {i} (Origen: {nombre_archivo}) ---\n"
            texto_formateado += f"{doc.page_content}\n\n"
            
        return texto_formateado

    def consultar(self, pregunta_usuario: str) -> FinancieroAgentResponse:
        """
        Método principal para procesar la pregunta del usuario a través del RAG.
        """
        logger.info(f"Procesando nueva consulta: '{pregunta_usuario}'")
        
        # Paso A: El retriever busca en la base de datos FAISS los pedazos de PDFs más similares
        logger.info("Buscando evidencias en los manuales de DEPORCA (FAISS)...")
        documentos_recuperados = self.retriever.invoke(pregunta_usuario)
        
        # Paso B: Convertir esos fragmentos de objetos Document a un solo string de texto
        contexto_texto = self._formatear_documentos(documentos_recuperados)
        
        # Paso C: Enviar el contexto y la pregunta a la cadena del LLM
        logger.info(f"Enviando contexto ({len(documentos_recuperados)} chunks) al LLM")
        try:
            # La respuesta ya viene parseada automáticamente como un objeto de AuditorAgentResponse
            respuesta_objeto: FinancieroAgentResponse = self.cadena.invoke({
                "contexto": contexto_texto,
                "pregunta": pregunta_usuario
            })
            return respuesta_objeto
            
        except Exception as e:
            logger.error(f"Error crítico durante la generación estructurada del LLM: {e}")
            raise e