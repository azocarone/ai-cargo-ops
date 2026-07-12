# modulo/motor_rag.py
import logging

# Obtener el logger específico de este módulo (antepone 'modulo.motor_rag')
logger = logging.getLogger(__name__)

class MotorRAGPrueba:
    """Clase encargada de gestionar las consultas de prueba hacia el LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        logger.info("MotorRAGPrueba inicializado correctamente con el LLM inyectado.")

    def ejecutar_consulta_lineal(self, pregunta: str) -> str:
        """Envía una pregunta al LLM y retorna el contenido de la respuesta."""
        try:
            # Usamos el logger del módulo en lugar de 'logging' global
            logger.info(f"Enviando consulta al modelo: '{pregunta}'")
            respuesta = self.llm.invoke(pregunta)
            
            logger.debug("Respuesta recibida exitosamente desde la API.")
            return respuesta.content
            
        except Exception as e:
            # Registramos el error con el contexto exacto de este módulo
            logger.error(f"Fallo al invocar el LLM desde MotorRAG: {e}")
            raise e