"""Módulo de fábrica e instanciación de agentes para LangGraph.

Este módulo implementa el patrón de diseño Factory mediante un enfoque
orientado a configuración (Data-Driven Creation). Permite desacoplar
la construcción dinámica de agentes (RAG o Directos) de la lógica de
orquestación del sistema.

Ejemplo:
    >>> agentes = inicializar_agentes(modo_dev=True, retriever_compartido=my_retriever)
    >>> orquestador = agentes["orquestador"]
"""

import logging
from typing import Any, Dict, List, Optional, Type, Union

from modulo.agent_direct import AgenteDirecto
from modulo.agent_rag import AgenteRAG
from modulo.prompts import (
    PROMPT_AUDITOR,
    PROMPT_BOT,
    PROMPT_FINANCIERO,
    PROMPT_ORQUESTADOR,
)
from modulo.schemes import (
    AuditorAgentResponse,
    BotAgentResponse,
    FinancieroAgentResponse,
    OrquestadorAgentResponse,
)

logger = logging.getLogger(__name__)

# Configuración estática que define el registro centralizado de agentes.
# Facilita la extensión sin necesidad de modificar la función de instanciación.
CONFIGURACION_AGENTES: List[Dict[str, Any]] = [
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

# Definición de alias para mejorar el tipado estático del retorno
InstanciaAgente = Union[AgenteDirecto, AgenteRAG]


def inicializar_agentes(
    modo_dev: bool,
    retriever_compartido: Optional[Any] = None,
) -> Dict[str, InstanciaAgente]:
    """Instancia dinámicamente el catálogo de agentes configurados en el módulo.

    Itera sobre `CONFIGURACION_AGENTES` construyendo los argumentos de
    inicialización requeridos por cada tipo de agente (`AgenteDirecto` o
    `AgenteRAG`). Garantiza que las dependencias obligatorias (como el
    retriever para arquitectura RAG) estén presentes antes de instanciar.

    Args:
        modo_dev (bool): Flag que habilita/deshabilita el comportamiento de
            depuración o verbosidad en los agentes instanciados.
        retriever_compartido (Optional[Any]): Instancia del retriever para los
            agentes que requieren recuperación de contexto (RAG). Deberá ser
            distinto de None si al menos un agente configurado requiere RAG.

    Returns:
        Dict[str, InstanciaAgente]: Mapeo dinámico cuyas llaves corresponden al
            identificador del agente (p. ej., 'orquestador', 'auditor') y cuyos
            valores son las instancias inicializadas.

    Raises:
        ValueError: Si algún agente con `requiere_retriever=True` es procesado
            y `retriever_compartido` es `None`.
    """
    logger.info("Iniciando la construcción dinámica de la jerarquía de agentes.")
    agentes_instanciados: Dict[str, InstanciaAgente] = {}

    for cfg in CONFIGURACION_AGENTES:
        # Mapeo unificado de parámetros requeridos por la firma base de los agentes
        kwargs: Dict[str, Any] = {
            "prompt_sistema": cfg["prompt"],
            "esquema_respuesta": cfg["esquema"],
            "nombre_agente": cfg["nombre"],
            "modo_desarrollo": modo_dev,
        }

        # Validación en tiempo de ejecución de inyección de dependencias RAG
        if cfg["requiere_retriever"]:
            if retriever_compartido is None:
                mensaje_error = (
                    f"Falta dependencia crítica: El agente '{cfg['nombre']}' "
                    f"requiere 'retriever_compartido', pero se recibió None."
                )
                logger.error(mensaje_error)
                raise ValueError(mensaje_error)

            kwargs["retriever"] = retriever_compartido

        # Instanciación polimórfica basada en el registro de configuración
        agentes_instanciados[cfg["clave"]] = cfg["clase"](**kwargs)
        logger.debug("Agente '%s' instanciado exitosamente.", cfg["nombre"])

    logger.info("Jerarquía de agentes construida correctamente (%d agentes).", len(agentes_instanciados))
    return agentes_instanciados