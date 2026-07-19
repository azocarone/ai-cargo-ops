import os
import logging
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

class GestorRAG:
    """
    Clase encargada del ciclo de vida del RAG: 
    Carga de PDFs, fragmentación, generación de embeddings e indexación en FAISS.
    """
    def __init__(self, ruta_assets: str = "../assets", chunk_size: int = 500, chunk_overlap: int = 50):
        self.ruta_assets = Path(ruta_assets)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retriever = None

    def _cargar_y_fragmentar_documentos(self):
        """Busca y procesa los PDFs en la ruta especificada."""
        if not self.ruta_assets.exists():
            raise FileNotFoundError(f"La ruta de assets no existe: {self.ruta_assets.resolve()}")
            
        docs = []
        for documento in self.ruta_assets.glob("*.pdf"):
            try:
                loader = PyMuPDFLoader(str(documento))
                docs.extend(loader.load())
                logger.info(f"📄 Archivo RAG cargado exitosamente: {documento.name}")
            except Exception as e:
                logger.error(f"❌ Error cargando archivo RAG {documento.name}: {e}")
                
        if not docs:
            logger.warning("⚠️ No se encontraron documentos PDF legítimos para alimentar el RAG.")
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )
        return splitter.split_documents(docs)

    def inicializar_base_vectores(self):
        """Construye el almacén vectorial FAISS y expone el objeto Retriever."""
        logger.info("Iniciando el proceso de indexación RAG...")
        chunks = self._cargar_y_fragmentar_documentos()
        
        if not chunks:
            raise RuntimeError("No se puede inicializar FAISS sin fragmentos de texto válidos.")

        # Inicializar los embeddings optimizados de NVIDIA
        embedder = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            nvidia_api_key=os.environ.get("NVIDIA_API_KEY")
        )
        
        logger.info(f"Generando vectores e indexando en FAISS ({len(chunks)} chunks)...")
        vectorstore = FAISS.from_documents(chunks, embedder)
        
        # Guardamos el buscador configurado con sus filtros
        self.retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.3, "k": 3}
        )
        logger.info("✅ Base de datos vectorial FAISS lista y operativa.")
        return self.retriever

    def obtener_retriever(self):
        """Devuelve el retriever configurado. Lanza error si no se ha inicializado."""
        if not self.retriever:
            raise RuntimeError("El RAG no ha sido inicializado. Ejecute primero 'inicializar_base_vectores()'")
        return self.retriever