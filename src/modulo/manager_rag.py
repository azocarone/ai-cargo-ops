"""
Módulo de Gestión de Arquitectura RAG (Retrieval-Augmented Generation).

Este módulo proporciona el componente `GestorRAG`, responsable de orquestar 
el ciclo de vida completo de un pipeline de ingesta vectorial:
    1. Descubrimiento y lectura de documentos en formato PDF.
    2. Segmentación de texto en fragmentos (chunks) optimizados.
    3. Generación de embeddings densos mediante APIs de NVIDIA.
    4. Indexación en un almacén vectorial en memoria (FAISS) y exposición 
       de un objeto Retriever de alta precisión.

Estándares aplicados: PEP 8, PEP 257 (Google Style Docstrings), Type Hinting (PEP 484).
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuración del logger del módulo para garantizar trazabilidad sin forzar handlers globales
logger = logging.getLogger(__name__)


class GestorRAG:
    """Orquesta la ingesta de documentos, embeddings e indexación para un pipeline RAG.

    Attributes:
        ruta_assets (Path): Ruta del directorio que contiene los archivos PDF.
        chunk_size (int): Tamaño máximo de caracteres por cada fragmento de texto.
        chunk_overlap (int): Solapamiento de caracteres entre fragmentos adyacentes.
        retriever (Optional[VectorStoreRetriever]): Objeto buscador configurado o None 
            si la base no ha sido inicializada.
    """

    def __init__(
        self, 
        ruta_assets: Union[str, Path] = "../assets", 
        chunk_size: int = 500, 
        chunk_overlap: int = 50
    ) -> None:
        """Inicializa la configuración básica del gestor RAG.

        Args:
            ruta_assets: Directorio raíz donde reposan los PDFs. Acepta `str` o `Path`.
            chunk_size: Límite superior de caracteres por chunk. Valor por defecto: 500.
            chunk_overlap: Caracteres compartidos entre chunks para preservar contexto 
                semántico en los límites del corte. Valor por defecto: 50.
        """
        # Garantizamos la normalización al tipo estándar Path de pathlib
        self.ruta_assets: Path = Path(ruta_assets)
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.retriever: Optional[VectorStoreRetriever] = None

    def _cargar_y_fragmentar_documentos(self) -> List[Document]:
        """Carga iterativamente archivos PDF y los divide en chunks navegables.

        Raises:
            FileNotFoundError: Si el directorio `ruta_assets` no existe en el sistema de archivos.

        Returns:
            List[Document]: Lista de objetos Document de LangChain procesados y divididos. 
            Retorna una lista vacía si no se lograron procesar PDFs válidos.
        """
        if not self.ruta_assets.exists():
            raise FileNotFoundError(f"La ruta de assets no existe: {self.ruta_assets.resolve()}")
            
        docs: List[Document] = []
        
        # Iteración resiliente: procesamos archivo por archivo para aislar fallos de IO/Corrupción
        for documento in self.ruta_assets.glob("*.pdf"):
            try:
                loader = PyMuPDFLoader(str(documento))
                docs.extend(loader.load())
                logger.info("📄 Archivo RAG cargado exitosamente: %s", documento.name)
            except Exception as e:
                # Captura de excepciones a nivel de archivo para evitar la caída masiva del pipeline
                logger.error("❌ Error cargando archivo RAG %s: %s", documento.name, e)
                
        if not docs:
            logger.warning("⚠️ No se encontraron documentos PDF legítimos para alimentar el RAG.")
            return []

        # Estrategia de fragmentación basada en separadores naturales (párrafos, frases, palabras)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )
        return splitter.split_documents(docs)

    def inicializar_base_vectores(self) -> VectorStoreRetriever:
        """Construye el almacén vectorial FAISS y genera el objeto Retriever asociativo.

        Valida que existan credenciales para la API de NVIDIA y fragmentos válidos 
        antes de realizar el costo computacional de vectorizar.

        Raises:
            KeyError: Si la variable de entorno `NVIDIA_API_KEY` no está definida.
            RuntimeError: Si la fase de fragmentación no produjo ningún documento.

        Returns:
            VectorStoreRetriever: Objeto Retriever listó para realizar búsquedas por similitud.
        """
        logger.info("Iniciando el proceso de indexación RAG...")
        
        # Validación temprana de precondición (Credenciales de API)
        nvidia_key = os.environ.get("NVIDIA_API_KEY")
        if not nvidia_key:
            raise KeyError(
                "La variable de entorno 'NVIDIA_API_KEY' no está definida. "
                "Es obligatoria para instanciar NVIDIAEmbeddings."
            )

        chunks = self._cargar_y_fragmentar_documentos()
        if not chunks:
            raise RuntimeError("No se puede inicializar FAISS sin fragmentos de texto válidos.")

        # Modelo de incrustación (Embedding) optimizado de NVIDIA
        embedder = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            nvidia_api_key=nvidia_key
        )
        
        logger.info("Generando vectores e indexando en FAISS (%d chunks)...", len(chunks))
        vectorstore = FAISS.from_documents(chunks, embedder)
        
        # Filtro por Umbral de Similitud: Descarta resultados con relevancia semántica < 0.15
        self.retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.15, "k": 3}
        )
        logger.info("✅ Base de datos vectorial FAISS lista y operativa.")
        return self.retriever

    def obtener_retriever(self) -> VectorStoreRetriever:
        """Devuelve la instancia activa del retriever.

        Raises:
            RuntimeError: Si se llama a este método antes de invocar `inicializar_base_vectores()`.

        Returns:
            VectorStoreRetriever: El retriever actualmente en memoria.
        """
        if self.retriever is None:
            raise RuntimeError(
                "El RAG no ha sido inicializado. Ejecute primero 'inicializar_base_vectores()'."
            )
        return self.retriever