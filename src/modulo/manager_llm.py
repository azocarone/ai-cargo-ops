"""Módulo de configuración e inicialización de LLMs de NVIDIA NIM.

Este módulo proporciona una abstracción para gestionar la instanciación de los
modelos de lenguaje de NVIDIA mediante ChatNVIDIA. Permite definir perfiles de
configuración adaptados a distintos entornos (Desarrollo y Producción) y
estrategias de Generación Aumentada por Recuperación (RAG) u orquestación.
"""

import logging
import os
from typing import Any, Dict, Final, Optional

from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Configuración del logger del módulo según las recomendaciones estándar de Python.
logger: logging.Logger = logging.getLogger(__name__)


class GestorLLM:
    """Administra la inicialización y parametrización de modelos NVIDIA NIM.

    Esta clase centraliza la configuración de hiperparámetros (temperatura,
    top_p, max_tokens, etc.) según el rol funcional del modelo en la
    arquitectura (p. ej., enrutador estricto, generación RAG o contexto masivo).

    Attributes:
        modo_desarrollo (bool): Indica si se ejecuta en entorno de desarrollo.
        modo_str (str): Representación en cadena del entorno ('DESARROLLO' o 'PRODUCCION').
        variante (str): Identificador del perfil de configuración seleccionado.
        nombre_modelo (str): Identificador del modelo en la plataforma NVIDIA NIM.
        max_tokens (int): Límite máximo de tokens de salida permitidos.
        pausa_preventiva (float): Tiempo de espera recomendado (en segundos) tras inferencia.
        descripcion_modelo (str): Explicación del propósito técnico de la variante.
        extra_args (Dict[str, Any]): Argumentos adicionales para la API (temperatura, top_p, etc.).
        nvidia_api_key (Optional[str]): Clave de API leída desde las variables de entorno.
        llm (ChatNVIDIA): Instancia activa del cliente de LangChain para NVIDIA.
    """

    # Diccionario de configuraciones constantes por entorno y perfil de uso.
    CONFIGURACION_MODELOS: Final[Dict[str, Dict[str, Dict[str, Any]]]] = {
        "DESARROLLO": {
            "predeterminado": {
                "nombre": "meta/llama-3.1-8b-instruct",
                "max_tokens": 1024,
                "pausa": 0.2,
                "descripcion": (
                    "Llama 3.1 8B - RAG Rápido, económico e ideal para "
                    "pruebas de lógica y prompts."
                ),
                "extra_args": {"temperature": 0.0},
            }
        },
        "PRODUCCION": {
            "ORQUESTADOR_ESTRICTO": {
                "nombre": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
                "max_tokens": 1024,
                "pausa": 0.5,
                "descripcion": (
                    "Optimizado para enrutamiento, clasificación y "
                    "extracción de variables sin variaciones."
                ),
                "extra_args": {
                    "temperature": 0.0,  # Determimismo absoluto para decisiones de ruteo
                    "top_p": 0.01,       # Restricción extrema de aleatoriedad
                },
            },
            "NVIDIA_RAG": {
                "nombre": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
                "max_tokens": 4096,
                "pausa": 1.0,
                "descripcion": (
                    "Nemotron Super 49B - Optimizado por NVIDIA para alineación "
                    "estricta en RAG y mitigación de alucinaciones."
                ),
                "extra_args": {
                    "temperature": 0.1,
                    "top_p": 0.90,
                },
            },
            "CONTEXTO_MASIVO": {
                "nombre": "meta/llama-3.1-70b-instruct",
                "max_tokens": 8192,
                "pausa": 1.5,
                "descripcion": (
                    "Llama 3.1 70B - Ventana de contexto masiva. Evita el "
                    "efecto 'perderse en el medio' con múltiples documentos."
                ),
                "extra_args": {
                    "temperature": 0.2,
                    "top_p": 0.95,
                },
            },
        },
    }

    def __init__(
        self,
        modo_desarrollo: bool = False,
        variante: str = "NVIDIA_RAG",
    ) -> None:
        """Inicializa el gestor y construye el cliente LLM según la variante.

        Args:
            modo_desarrollo: Si es True, fuerza el uso del entorno 'DESARROLLO'
                y la variante 'predeterminado'. Por defecto es False.
            variante: Nombre de la variante a utilizar en entorno de 'PRODUCCION'
                (ej. 'ORQUESTADOR_ESTRICTO', 'NVIDIA_RAG', 'CONTEXTO_MASIVO').

        Raises:
            ValueError: Si la variante no existe en la configuración o si la API key falta.
            RuntimeError: Si la instanciación del cliente `ChatNVIDIA` falla.
        """
        self.modo_desarrollo: bool = modo_desarrollo
        self.modo_str: str = "DESARROLLO" if self.modo_desarrollo else "PRODUCCION"
        self.variante: str = "predeterminado" if self.modo_desarrollo else variante.upper()

        # Validación temprana de existencia de la clave seleccionada
        if self.variante not in self.CONFIGURACION_MODELOS[self.modo_str]:
            opciones = list(self.CONFIGURACION_MODELOS[self.modo_str].keys())
            raise ValueError(
                f"Variante '{variante}' no válida para el modo {self.modo_str}. "
                f"Opciones disponibles: {opciones}"
            )

        # Atributos que serán inicializados en los métodos privados
        self.nombre_modelo: str = ""
        self.max_tokens: int = 0
        self.pausa_preventiva: float = 0.0
        self.descripcion_modelo: str = ""
        self.extra_args: Dict[str, Any] = {}
        self.nvidia_api_key: Optional[str] = None

        # Carga secuencial y desacoplada del pipeline de inicialización
        self._cargar_configuracion()
        self._validar_credenciales()
        self.llm: ChatNVIDIA = self._inicializar_cliente()

    def _cargar_configuracion(self) -> None:
        """Extrae los hiperparámetros y metadatos del perfil activo."""
        datos_config = self.CONFIGURACION_MODELOS[self.modo_str][self.variante]

        self.nombre_modelo = datos_config["nombre"]
        self.max_tokens = datos_config["max_tokens"]
        self.pausa_preventiva = datos_config["pausa"]
        self.descripcion_modelo = datos_config["descripcion"]
        self.extra_args = datos_config["extra_args"]

        self.nvidia_api_key = os.environ.get("NVIDIA_API_KEY")

    def _validar_credenciales(self) -> None:
        """Valida que la credencial del servicio de NVIDIA esté disponible en el entorno.

        Raises:
            ValueError: Si `NVIDIA_API_KEY` no está definida o se encuentra vacía.
        """
        if not self.nvidia_api_key:
            raise ValueError(
                "La variable de entorno 'NVIDIA_API_KEY' no está definida o está vacía. "
                "Asegúrese de cargar el entorno correctamente antes de instanciar GestorLLM."
            )

        # Advertencia preventiva por longitud fuera de estándar para evitar fallos de red confusos
        if len(self.nvidia_api_key) < 10:
            logger.warning(
                "La 'NVIDIA_API_KEY' detectada es inusualmente corta. "
                "Podría generar fallos de autenticación con el SDK."
            )

    def _inicializar_cliente(self) -> ChatNVIDIA:
        """Instancia la clase cliente del SDK de LangChain manejando posibles excepciones.

        Returns:
            ChatNVIDIA: Objeto del cliente inicializado y listo para invocación.

        Raises:
            RuntimeError: Encapsula cualquier excepción proveniente del SDK para abstraer
                el error hacia la capa superior de la aplicación.
        """
        try:
            return ChatNVIDIA(
                model=self.nombre_modelo,
                nvidia_api_key=self.nvidia_api_key,
                max_completion_tokens=self.max_tokens,
                timeout=240,
                **self.extra_args,
            )
        except Exception as e:
            logger.error(
                f"Error crítico al instanciar ChatNVIDIA para el modelo '{self.nombre_modelo}': {e}"
            )
            raise RuntimeError(
                f"No se pudo crear el cliente LLM debido a un fallo en el SDK: {e}"
            ) from e

    def obtener_llm(self) -> ChatNVIDIA:
        """Registra los metadatos de ejecución y retorna la instancia del LLM.

        Returns:
            ChatNVIDIA: Instancia activa del modelo.
        """
        self.registrar_info()
        return self.llm

    def registrar_info(self) -> None:
        """Emite por el sistema de logs el estado y configuración actual del modelo."""
        logger.info("⚙️ [RAG GENERATOR] Modo: %s | Estrategia: %s", self.modo_str, self.variante)
        logger.info("🤖 [MODELO] %s", self.nombre_modelo)
        logger.info("💡 [PROPÓSITO] %s", self.descripcion_modelo)
        logger.info("⏱️ [CONTROL] Pausa sugerida post-recuperación: %.2fs", self.pausa_preventiva)