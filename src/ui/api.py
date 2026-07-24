"""Módulo de API REST para el sistema multi-agente de DEPORCA.

Este módulo expone un servicio web basado en FastAPI para interactuar con el
grafo de orquestación de LangGraph de forma asíncrona mediante peticiones HTTP.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, AsyncGenerator
import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Importaciones de infraestructura local y componentes del sistema
from modulo.agents_factory import inicializar_agentes
from modulo.builder import crear_grafo_deporca
from modulo.manager_rag import GestorRAG


# =====================================================================
# CONFIGURACIÓN DE LOGGING Y ENTORNO
# =====================================================================

def inicializar_entorno() -> logging.Logger:
    """Carga variables de entorno y configura el sistema de logs."""
    load_dotenv()
    nivel_env: str = os.environ.get("LOG_LEVEL", "INFO").upper()
    niveles_validos: Dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    nivel_logging: int = niveles_validos.get(nivel_env, logging.INFO)

    logging.basicConfig(
        level=nivel_logging,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("api_deporca")


logger = inicializar_entorno()


# =====================================================================
# MODELOS DE DATOS (PYDANTIC SCHEMAS)
# =====================================================================

class ConsultaUsuarioRequest(BaseModel):
    """Esquema de entrada para las consultas enviadas al sistema."""
    pregunta: str = Field(
        ...,
        min_length=1,
        description="Consulta enviada por el usuario.",
        example="¿Cuál es el saldo pendiente de la orden X?"
    )


class ConsultaUsuarioResponse(BaseModel):
    """Esquema de respuesta devuelto por la API."""
    pregunta: str
    respuesta_final: str
    estado_ejecucion: str = "exitoso"


# =====================================================================
# CICLO DE VIDA DE LA APLICACIÓN (LIFESPAN)
# =====================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona la inicialización y liberación de recursos pesados del sistema.
    
    Carga el RAG, instancia los agentes y compila el grafo LangGraph al iniciar
    la aplicación, dejándolos disponibles en `app.state` durante la sesión.
    """
    logger.info("Iniciando infraestructura de la API Multi-Agente...")

    modo_dev: bool = os.environ.get("MODO_DESARROLLO", "False").lower() in ("true", "1", "t")

    # 1. Configuración del subsistema RAG
    logger.info("Cargando base vectorial y RAG...")
    rag = GestorRAG(ruta_assets="../assets")
    retriever_compartido = rag.inicializar_base_vectores()

    # 2. Instanciación de Agentes
    logger.info("Instanciando jerarquía de agentes...")
    agentes_instanciados = inicializar_agentes(modo_dev, retriever_compartido)

    # 3. Compilación del Grafo LangGraph
    logger.info("Compilando Grafo de LangGraph...")
    grafo_app = crear_grafo_deporca()

    # Guardar estado global en la app de FastAPI
    app.state.agentes = agentes_instanciados
    app.state.grafo = grafo_app

    logger.info("🚀 API DEPORCA lista para recibir peticiones.")
    
    yield  # La aplicación corre en este punto

    logger.info("Apagando la API DEPORCA...")


# =====================================================================
# INICIALIZACIÓN DE FASTAPI Y ENDPOINTS
# =====================================================================

app = FastAPI(
    title="DEPORCA Multi-Agent API",
    description="Backend de servicios REST para la orquestación de agentes con LangGraph.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Endpoint para verificar que el servicio está activo."""
    return {"status": "ok", "sistema": "DEPORCA Multi-Agente"}


@app.post(
    "/api/v1/consultar",
    response_model=ConsultaUsuarioResponse,
    status_code=status.HTTP_200_OK
)
async def procesar_consulta(payload: ConsultaUsuarioRequest) -> ConsultaUsuarioResponse:
    """Procesa una pregunta del usuario mediante el grafo multi-agente."""
    try:
        # Recuperar dependencias inicializadas del estado global
        agentes_instanciados = app.state.agentes
        grafo = app.state.grafo

        # Construcción del estado inicial del grafo
        estado_inicial: Dict[str, Any] = {
            "pregunta_usuario": payload.pregunta.strip(),
            "agentes": agentes_instanciados,
            "payload_orquestador": None,
            "respuesta_auditor": None,
            "respuesta_financiero": None,
            "respuesta_bot": None,
            "respuesta_final": "",
        }

        # Ejecución sincrónica invocada dentro del contexto asíncrono
        resultado: Dict[str, Any] = grafo.invoke(estado_inicial)

        respuesta_texto = resultado.get(
            "respuesta_final", 
            "El sistema no generó una respuesta adecuada."
        )

        return ConsultaUsuarioResponse(
            pregunta=payload.pregunta,
            respuesta_final=respuesta_texto
        )

    except Exception as exc:
        logger.error(f"Error procesando la consulta: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno al procesar la solicitud con el sistema multi-agente."
        )