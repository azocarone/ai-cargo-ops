"""Módulo base para la construcción de agentes de IA estructurados con LangChain.

Proporciona la clase genérica `AgenteBase`, encargada de orquestar la integración
entre un modelo de lenguaje (LLM), plantillas de prompts de LangChain y esquemas
de salida estructurada (por ejemplo, Pydantic models).
"""

import logging
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from langchain_core.prompts import ChatPromptTemplate

from modulo.manager_llm import GestorLLM

# Tipo genérico para garantizar el tipado dinámico de los esquemas de respuesta.
T = TypeVar("T")


class AgenteBase(Generic[T]):
    """Clase base genérica para la orquestación de agentes con salida estructurada.

    Esta clase abstrae la configuración de un modelo de lenguaje (LLM),
    combinando una plantilla de prompt con la capacidad del modelo para retornar
    objetos fuertemente tipados definidos por el desarrollador.

    Attributes:
        esquema_respuesta (Type[T]): Modelo/Clase que define la estructura
            esperada en la respuesta del LLM.
        logger (logging.Logger): Instancia del registrador para seguimiento de
            eventos de auditoría y depuración.
        prompt_template (ChatPromptTemplate): Plantilla configurada para formatear
            los mensajes hacia el LLM.
        cadena (Runnable): Cadena ejecutable de LangChain (Prompt | LLM
            estructurado).
    """

    def __init__(
        self,
        prompt_sistema: str,
        esquema_respuesta: Type[T],
        nombre_agente: Optional[str] = None,
        modo_desarrollo: bool = False,
    ) -> None:
        """Inicializa los componentes principales del agente de IA.

        Args:
            prompt_sistema: Instrucciones base del sistema que guiarán el
                comportamiento del LLM.
            esquema_respuesta: Tipo o modelo Pydantic que representará el
                formato de salida esperado.
            nombre_agente: Nombre opcional para identificar el logger del
                agente. Si es None, usará el nombre de la clase.
            modo_desarrollo: Determina si el motor de LLM debe ejecutarse
                en entorno local/desarrollo.
        """
        self.esquema_respuesta = esquema_respuesta

        id_logger = nombre_agente or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{id_logger}")

        self.logger.info("Inicializando el motor de IA")
        llm = GestorLLM(modo_desarrollo=modo_desarrollo)
        llm_base = llm.obtener_llm()

        # Vincula el esquema de respuesta al modelo base mediante LangChain.
        self.llm_estructurado = llm_base.with_structured_output(esquema_respuesta)

        # Construcción y composición de la cadena de procesamiento mediante el operador '|'
        self.prompt_template = self._crear_prompt_template(prompt_sistema)
        self.cadena = self.prompt_template | self.llm_estructurado

    def _crear_prompt_template(self, prompt_sistema: str) -> ChatPromptTemplate:
        """Crea la plantilla base de mensajes para la interacción con el modelo.

        Args:
            prompt_sistema: Instrucción inicial asignada al rol 'system'.

        Returns:
            ChatPromptTemplate: Plantilla de LangChain configurada.
        """
        return ChatPromptTemplate.from_messages(
            [
                ("system", prompt_sistema),
                (
                    "user",
                    "CONTEXTO DE REFERENCIA:\n{contexto}\n\nPREGUNTA USUARIO: {pregunta}",
                ),
            ]
        )

    def _preparar_payload(self, pregunta_usuario: str) -> Dict[str, Any]:
        """Prepara el diccionario de variables requeridas por la plantilla de prompt.

        Este método debe ser implementado obligatoriamente por las subclases
        para construir los parámetros dinámicos (p. ej., 'contexto', 'pregunta')
        esperados por la plantilla del agente.

        Args:
            pregunta_usuario: Consulta realizada por el usuario.

        Returns:
            Dict[str, Any]: Diccionario con el payload listo para invocación.

        Raises:
            NotImplementedError: Si la subclase no sobrescribe este método.
        """
        raise NotImplementedError(
            "Las subclases deben implementar el método '_preparar_payload'."
        )

    def consultar(self, pregunta_usuario: str) -> T:
        """Ejecuta la consulta hacia la cadena de IA y retorna la respuesta estructurada.

        Aplica polimorfismo delegando la construcción de los datos de entrada
         al método `_preparar_payload` implementado por la subclase.

        Args:
            pregunta_usuario: Entrada textual o consulta formulada por el usuario.

        Returns:
            T: Instancia del tipo `esquema_respuesta` con la respuesta procesada.

        Raises:
            Exception: Re-lanza cualquier excepción ocurrida durante la invocación
                del LLM tras registrarla en los logs.
        """
        self.logger.info(f"Procesando nueva consulta: '{pregunta_usuario}'")

        # Invocación polimórfica: la subclase activa determina cómo armar los datos
        payload = self._preparar_payload(pregunta_usuario)

        try:
            respuesta_objeto: T = self.cadena.invoke(payload)
            return respuesta_objeto
        except Exception as e:
            self.logger.error(f"Error crítico en la ejecución del agente: {e}")
            raise