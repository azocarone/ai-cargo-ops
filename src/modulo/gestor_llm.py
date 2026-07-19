"""
Módulo de configuración para Modelos de Lenguaje (LLM) de NVIDIA NIM.

Este módulo gestiona la inicialización optimizada de los modelos de NVIDIA,
configurados específicamente como 'Generadores' en arquitecturas RAG.
"""

import os
import logging
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Obtener el logger específico de este módulo
logger = logging.getLogger(__name__)

class GestorLLM:
    """
    Clase encargada de inicializar y parametrizar los modelos de NVIDIA NIM
    según la estrategia RAG requerida (Desarrollo o Producción).
    """

    CONFIGURACION_MODELOS = {
        "DESARROLLO": {
            "predeterminado": {
                "nombre": "meta/llama-3.1-8b-instruct",
                "max_tokens": 1024,
                "pausa": 0.2,
                "descripcion": "Llama 3.1 8B - RAG Rápido, económico e ideal para pruebas de lógica y prompts.",
                "extra_args": {}
            }
        },
        "PRODUCCION": {
            "NVIDIA_RAG": {
                "nombre": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
                "max_tokens": 4096,
                "pausa": 1.0,
                "descripcion": "Nemotron Super 49B - Optimizado por NVIDIA para alineación estricta en RAG y mitigación de alucinaciones.",
                "extra_args": {
                    "temperature": 0.1,
                    "top_p": 0.90
                }
            },
            "CONTEXTO_MASIVO": {
                "nombre": "meta/llama-3.1-70b-instruct",
                "max_tokens": 8192,
                "pausa": 1.5,
                "descripcion": "Llama 3.1 70B - Ventana de contexto masiva. Evita el efecto 'perderse en el medio' con múltiples PDFs.",
                "extra_args": {
                    "temperature": 0.2,
                    "top_p": 0.95
                }
            }
        }
    }

    def __init__(self, modo_desarrollo: bool = False, variante: str = "NVIDIA_RAG"):
        """
        Inicializa el generador de NVIDIA según el entorno y la estrategia RAG.
        
        Raises:
            ValueError: Si la variante no es válida o si falta la firma de autenticación.
            RuntimeError: Si el cliente de ChatNVIDIA falla al inicializarse.
        """
        self.modo_desarrollo = modo_desarrollo
        self.modo_str = "DESARROLLO" if self.modo_desarrollo else "PRODUCCION"
        self.variante = "predeterminado" if self.modo_desarrollo else variante.upper()
        
        if self.variante not in self.CONFIGURACION_MODELOS[self.modo_str]:
            opciones = list(self.CONFIGURACION_MODELOS[self.modo_str].keys())
            raise ValueError(f"Variante '{variante}' no válida para el modo {self.modo_str}. Opciones: {opciones}")

        # Ejecutar cargas secuenciales controladas
        self._cargar_configuracion()
        self._validar_credenciales()
        self.llm = self._inicializar_cliente()

    def _cargar_configuracion(self):
        """Extrae los parámetros del diccionario según el rol asignado."""
        datos_config = self.CONFIGURACION_MODELOS[self.modo_str][self.variante]
        
        self.nombre_modelo = datos_config["nombre"]
        self.max_tokens = datos_config["max_tokens"]
        self.pausa_preventiva = datos_config["pausa"]
        self.descripcion_modelo = datos_config["descripcion"]
        self.extra_args = datos_config["extra_args"]
        
        # Leemos la variable de entorno
        self.nvidia_api_key = os.environ.get("NVIDIA_API_KEY")

    def _validar_credenciales(self):
        """
        Valida de forma temprana la presencia de la API Key indispensables.
        Previene fallos silenciosos o conexiones truncadas.
        """
        if not self.nvidia_api_key:
            raise ValueError(
                "La variable de entorno 'NVIDIA_API_KEY' no está definida o está vacía. "
                "Asegúrese de cargar el archivo .env correctamente antes de inicializar esta clase."
            )
        
        # Alerta preventiva en logs si se detecta una clave sospechosamente corta
        if len(self.nvidia_api_key) < 10:
            logger.warning("La 'NVIDIA_API_KEY' detectada es inusualmente corta. Podría causar problemas de autenticación.")

    def _inicializar_cliente(self) -> ChatNVIDIA:
        """Instancia el cliente ChatNVIDIA mitigando excepciones del SDK."""
        try:
            return ChatNVIDIA(
                model=self.nombre_modelo,
                nvidia_api_key=self.nvidia_api_key,
                max_completion_tokens=self.max_tokens,
                timeout=240,
                **self.extra_args
            )
        except Exception as e:
            logger.error(f"Error crítico al instanciar ChatNVIDIA para el modelo {self.nombre_modelo}: {e}")
            raise RuntimeError(f"No se pudo crear el cliente LLM debido a un fallo del SDK: {e}") from e

    def obtener_llm(self) -> ChatNVIDIA:
        """Retorna la instancia del Generador (LLM) configurado."""
        self.registrar_info()
        return self.llm

    def registrar_info(self):
        """
        Reemplaza al antiguo info(). Envía los metadatos del modelo al flujo
        de logs en lugar de forzar una salida por pantalla (print).
        """
        logger.info(f"⚙️ [RAG GENERATOR] Modo: {self.modo_str} | Estrategia: {self.variante}")
        logger.info(f"🤖 [MODELO] {self.nombre_modelo}")
        logger.info(f"💡 [PROPÓSITO] {self.descripcion_modelo}")
        logger.info(f"⏱️ [CONTROL] Pausa sugerida post-recuperación: {self.pausa_preventiva}s")