"""
Módulo de configuración para Modelos de Lenguaje (LLM) de NVIDIA NIM.

Este módulo gestiona la inicialización optimizada de los modelos de NVIDIA,
configurados específicamente como 'Generadores' en arquitecturas RAG.

================================================================================
PRERREQUISITOS (DEPENDENCIAS)
================================================================================
    $ pip install -qU langchain-nvidia-ai-endpoints

================================================================================
CONFIGURACIÓN DE ENTORNO
================================================================================
Requiere la declaración de la siguiente credencial en el entorno del sistema:
NVIDIA_API_KEY = "tu_api_key_aquí"
"""

import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA

class ConfiguracionLLMNvidia:
    """
    Clase encargada de inicializar y parametrizar los modelos de NVIDIA NIM
    según la estrategia RAG requerida (Desarrollo o Producción).

    Ejemplo de uso:
        >>> from modulo.configuracion_llm_nvidia import ConfiguracionLLMNvidia
        >>> config = ConfiguracionLLMNvidia(modo_desarrollo=False, variante="NVIDIA_RAG")
        >>> llm = config.obtener_llm()
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
                    "temperature": 0.1,  # Temperatura baja para respuestas más factuales y ceñidas al contexto
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

        Args:
            modo_desarrollo (bool): True para usar el modelo ágil de desarrollo. False para producción.
            variante (str): Estrategia en producción ('NVIDIA_RAG' o 'CONTEXTO_MASIVO').
        
        Raises:
            ValueError: Si la variante elegida no coincide con el modo seleccionado.
        """
        self.modo_desarrollo = modo_desarrollo
        self.modo_str = "DESARROLLO" if self.modo_desarrollo else "PRODUCCION"
        
        # Normalizar la variante elegida
        self.variante = "predeterminado" if self.modo_desarrollo else variante.upper()
        
        # Validar configuración antes de proceder
        if self.variante not in self.CONFIGURACION_MODELOS[self.modo_str]:
            opciones = list(self.CONFIGURACION_MODELOS[self.modo_str].keys())
            raise ValueError(f"Variante '{variante}' no válida para el modo {self.modo_str}. Opciones disponibles: {opciones}")

        self._cargar_configuracion()
        self.llm = self._inicializar_cliente()

    def _cargar_configuracion(self):
        """Extrae los parámetros del diccionario según el rol asignado."""
        datos_config = self.CONFIGURACION_MODELOS[self.modo_str][self.variante]
        
        self.nombre_modelo = datos_config["nombre"]
        self.max_tokens = datos_config["max_tokens"]
        self.pausa_preventiva = datos_config["pausa"]
        self.descripcion_modelo = datos_config["descripcion"]
        self.extra_args = datos_config["extra_args"]
        
        # Token de autenticación indispensable para NVIDIA NIM
        self.nvidia_api_key = os.environ.get("NVIDIA_API_KEY")

    def _inicializar_cliente(self) -> ChatNVIDIA:
        """Instancia el cliente ChatNVIDIA inyectando los argumentos específicos del modelo."""
        return ChatNVIDIA(
            model=self.nombre_modelo,
            nvidia_api_key=self.nvidia_api_key,
            max_completion_tokens=self.max_tokens,
            timeout=240,  # Prevención de Timeouts en contextos densos de RAG
            **self.extra_args
        )

    def obtener_llm(self) -> ChatNVIDIA:
        """Retorna la instancia del Generador (LLM) configurado."""
        return self.llm

    def info(self):
        """Imprime un desglose claro del rol y las capacidades del modelo seleccionado."""
        print(f"⚙️ [RAG GENERATOR] Modo: {self.modo_str} | Estrategia: {self.variante}")
        print(f"🤖 [MODELO] {self.nombre_modelo}")
        print(f"💡 [PROPÓSITO] {self.descripcion_modelo}")
        print(f"⏱️ [CONTROL] Pausa sugerida post-recuperación: {self.pausa_preventiva}s")