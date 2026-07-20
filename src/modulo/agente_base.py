import logging
from typing import Type, TypeVar, Generic, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from modulo.gestor_llm import GestorLLM

T = TypeVar('T')

class AgenteBase(Generic[T]):
    def __init__(self, prompt_sistema: str, esquema_respuesta: Type[T], nombre_agente: str = None, modo_desarrollo: bool = False):
        self.esquema_respuesta = esquema_respuesta
        
        id_logger = nombre_agente or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{id_logger}")
        
        self.logger.info("Inicializando el motor de IA")
        llm = GestorLLM(modo_desarrollo=modo_desarrollo)
        llm_base = llm.obtener_llm()
        self.llm_estructurado = llm_base.with_structured_output(esquema_respuesta)
        
        # El molde base se puede adaptar o sobrescribir si es necesario
        self.prompt_template = self._crear_prompt_template(prompt_sistema)
        self.cadena = self.prompt_template | self.llm_estructurado

    def _crear_prompt_template(self, prompt_sistema: str) -> ChatPromptTemplate:
        # Por defecto asume la estructura con contexto, pero las subclases pueden cambiarlo
        return ChatPromptTemplate.from_messages([
            ("system", prompt_sistema),
            ("user", "CONTEXTO DE REFERENCIA:\n{contexto}\n\nPREGUNTA USUARIO: {pregunta}")
        ])

    def _preparar_payload(self, pregunta_usuario: str) -> Dict[str, Any]:
        """
        Método abstracto/base. Las subclases DEBEN sobrescribir este método
        para armar el diccionario que espera el prompt.
        """
        raise NotImplementedError("Las subclases deben implementar _preparar_payload")

    def consultar(self, pregunta_usuario: str) -> T:
        self.logger.info(f"Procesando nueva consulta: '{pregunta_usuario}'")
        
        # Aquí ocurre la magia del polimorfismo:
        # Python llamará dinámicamente al método de la subclase activa
        payload = self._preparar_payload(pregunta_usuario)
        
        try:
            respuesta_objeto: T = self.cadena.invoke(payload)
            return respuesta_objeto
        except Exception as e:
            self.logger.error(f"Error crítico en la ejecución: {e}")
            raise e