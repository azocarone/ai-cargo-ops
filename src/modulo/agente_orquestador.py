import logging
from modulo.gestor_llm import GestorLLM
from modulo.esquemas import OrquestadorAgentResponse
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from modulo.prompts import PROMPT_ORQUESTADOR

logger = logging.getLogger(__name__)

class AgenteOrquestador:
    def __init__(self, modo_desarrollo: bool=False):
        logger.info("Inicializando el motor de IA")
        llm = GestorLLM(modo_desarrollo=modo_desarrollo)
        llm_base = llm.obtener_llm()

        self.llm_estructurado = llm_base.with_structured_output(OrquestadorAgentResponse)
    
    def consultar(self, pregunta_usuario: str) -> OrquestadorAgentResponse:
        logger.info(f"Procesando nueva consulta: '{pregunta_usuario}'")
        respuesta_objeto = self.llm_estructurado.invoke([
            SystemMessage(content=PROMPT_ORQUESTADOR),
            HumanMessage(content=pregunta_usuario)
        ])
        return respuesta_objeto
