"""
agents_factory.py - Configuración declarativa e instanciación de agentes
"""
import logging

# Importaciones de agentes polimórficos
from modulo.agent_direct import AgenteDirecto
from modulo.agent_rag import AgenteRAG

from modulo.prompts import (
    PROMPT_ORQUESTADOR,
    PROMPT_AUDITOR,
    PROMPT_FINANCIERO,
    PROMPT_BOT,
)

from modulo.schemes import (
    OrquestadorAgentResponse,
    AuditorAgentResponse,
    FinancieroAgentResponse,
    BotAgentResponse,
)

logger = logging.getLogger(__name__)

# Diccionario central que almacenará los agentes una vez instanciados
AGENTS = {}

# Matriz de configuración declarativa (Data-Driven)
CONFIGURACION_AGENTES = [
    {
        "clave": "orquestador",
        "clase": AgenteDirecto,
        "nombre": "Orquestador",
        "prompt": PROMPT_ORQUESTADOR,
        "esquema": OrquestadorAgentResponse,
        "requiere_retriever": False,
    },
    {
        "clave": "auditor",
        "clase": AgenteRAG,
        "nombre": "Auditor",
        "prompt": PROMPT_AUDITOR,
        "esquema": AuditorAgentResponse,
        "requiere_retriever": True,
    },
    {
        "clave": "financiero",
        "clase": AgenteRAG,
        "nombre": "Financiero",
        "prompt": PROMPT_FINANCIERO,
        "esquema": FinancieroAgentResponse,
        "requiere_retriever": True,
    },
    {
        "clave": "bot",
        "clase": AgenteDirecto,
        "nombre": "Bot",
        "prompt": PROMPT_BOT,
        "esquema": BotAgentResponse,
        "requiere_retriever": False,
    },
]


def inicializar_agentes(modo_dev: bool, retriever_compartido):
    """Instancia dinámicamente los agentes a partir del diccionario de configuración."""
    logger.info("Instanciando la jerarquía de agentes...")

    for cfg in CONFIGURACION_AGENTES:
        kwargs = {
            "prompt_sistema": cfg["prompt"],
            "esquema_respuesta": cfg["esquema"],
            "nombre_agente": cfg["nombre"],
            "modo_desarrollo": modo_dev,
        }

        if cfg["requiere_retriever"]:
            if retriever_compartido is None:
                raise ValueError(
                    f"El agente '{cfg['nombre']}' requiere un retriever válido."
                )
            kwargs["retriever"] = retriever_compartido

        # Se guardan en el diccionario global 'AGENTS'
        AGENTS[cfg["clave"]] = cfg["clase"](**kwargs)