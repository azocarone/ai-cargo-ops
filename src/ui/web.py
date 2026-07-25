"""Módulo de Interfaz Web basada en Streamlit para la empresa DEPORCA.

Este módulo define la arquitectura de la interfaz gráfica interactiva utilizando
Streamlit. Proporciona una experiencia visual tematizada para la gestión de
operaciones portuarias y logística marítima, integrando la ejecución del
grafo orquestador de agentes (LangGraph).

Estilo visual: Paleta naviera/marítima (#0A2540, #003366, #D4AF37).
"""

from typing import Any, Dict, List, TypedDict

import streamlit as st


class AgenteInfo(TypedDict):
    """Estructura de datos para los metadatos visuales de un agente."""

    icono: str
    nombre: str
    rol: str


class EstadoGrafo(TypedDict, total=False):
    """Estructura de datos del estado mutable esperado por el grafo de agentes."""

    pregunta_usuario: str
    agentes: Dict[str, Any]
    payload_orquestador: Any
    respuesta_auditor: Any
    respuesta_financiero: Any
    respuesta_bot: Any
    respuesta_final: str


class InterfazWebStreamlit:
    """Clase encargada de construir y gestionar la interfaz web en Streamlit[cite: 1].
    
    Encapsula la configuración visual, la barra lateral con información del
    sistema y el flujo interactivo de mensajes del chat con el grafo de agentes[cite: 1].
    """

    def __init__(self, app_grafo: Any, agentes: Dict[str, Any]) -> None:
        """Inicializa la interfaz con el grafo de agentes compilado y sus dependencias[cite: 1].

        Args:
            app_grafo (Any): Instancia del grafo de LangGraph compilado listo
                para invocar[cite: 1].
            agentes (Dict[str, Any]): Diccionario que contiene las instancias
                de los subagentes especializados[cite: 1].
        """
        self.app = app_grafo
        self.agentes = agentes

    def _aplicar_estilos_maritimos(self) -> None:
        """Inyecta reglas CSS personalizadas en la aplicación Streamlit[cite: 1].

        Ajusta la tipografía, colores del tema portuario de DEPORCA y garantiza
        la legibilidad adecuada en las tarjetas de chat y elementos de la barra
        lateral superando los estilos predeterminados de Streamlit[cite: 1].
        """
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            /* Contenedor principal */
            .stApp {
                background-color: #f4f7f9;
            }

            /* Encabezado DEPORCA */
            .deporca-header {
                background: linear-gradient(135deg, #0A2540 0%, #003366 60%, #1A4B84 100%);
                color: #FFFFFF !important;
                padding: 24px 30px;
                border-radius: 12px;
                margin-bottom: 25px;
                box-shadow: 0 4px 15px rgba(10, 37, 64, 0.15);
                border-bottom: 4px solid #D4AF37;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .deporca-title {
                font-size: 24px;
                font-weight: 700;
                color: #FFFFFF !important;
            }

            .deporca-subtitle {
                font-size: 13px;
                color: #B0C4DE !important;
                margin-top: 4px;
            }

            /* Componente de chat: Adaptación para alto contraste y legibilidad */
            [data-testid="stChatMessage"] {
                background-color: #FFFFFF !important;
                border-radius: 10px !important;
                border: 1px solid #E2E8F0 !important;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            }

            [data-testid="stChatMessage"] p,
            [data-testid="stChatMessage"] li,
            [data-testid="stChatMessage"] span,
            [data-testid="stChatMessage"] div {
                color: #1E293B !important;
            }

            [data-testid="stChatMessage"] code {
                background-color: #E2E8F0 !important;
                color: #0F172A !important;
                font-weight: 600 !important;
            }

            /* Barra lateral y tarjetas informativas */
            [data-testid="stSidebar"] {
                background-color: #0A2540 !important;
            }

            .agent-card {
                background-color: #FFFFFF !important;
                border-left: 4px solid #D4AF37 !important;
                padding: 10px 14px;
                border-radius: 6px;
                margin-bottom: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }

            .agent-name {
                font-weight: 600;
                color: #0A2540 !important;
                font-size: 13px;
            }

            .agent-desc {
                font-size: 11px;
                color: #475569 !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _renderizar_sidebar(self) -> None:
        """Construye la sección lateral (sidebar) de la aplicación[cite: 1].

        Muestra el panel de control con la lista de agentes activos, métricas
        de estado del sistema y la opción para reiniciar la sesión[cite: 1].
        """
        with st.sidebar:
            st.markdown("### ⚓ DEPORCA Control Center")
            st.markdown("**Almacenes y Depósitos Integrales Portuarios**")
            st.divider()

            st.markdown("#### 🚢 Flota Multi-Agente Activa")

            # Lista de agentes expuestos en el panel visual
            agentes_info: List[AgenteInfo] = [
                {
                    "icono": "🎯",
                    "nombre": "Agente Orquestador",
                    "rol": "Clasificación y Enrutamiento",
                },
                {
                    "icono": "📊",
                    "nombre": "Agente Financiero",
                    "rol": "Costos, Facturas y Tarifas",
                },
                {
                    "icono": "🔍",
                    "nombre": "Agente Auditor",
                    "rol": "Normativa y Verificación RAG",
                },
                {
                    "icono": "🤖",
                    "nombre": "Agente General",
                    "rol": "Asistencia Portuaria General",
                },
            ]

            # Inyección limpia de las tarjetas visuales por cada agente
            for info in agentes_info:
                st.markdown(
                    f"""
                    <div class="agent-card">
                        <div class="agent-name">{info['icono']} {info['nombre']}</div>
                        <div class="agent-desc">{info['rol']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.divider()

            st.markdown("#### 📦 Estado del Sistema")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="RAG Vectorial", value="Activo 🟢")
            with col2:
                st.metric(label="Grafo", value="Online ⚡")

            st.divider()

            # Mecanismo de reinicio de la conversación mediante la gestión de estado
            if st.button("🗑️ Limpiar Conversación", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    def renderizar(self) -> None:
        """Punto de entrada principal para renderizar la interfaz completa[cite: 1].

        Configura la página de Streamlit, aplica los temas, renderiza el
        historial de chat y procesa las nuevas preguntas enviando el estado al
        grafo de agentes[cite: 1].
        """
        st.set_page_config(
            page_title="DEPORCA - Control Portuario Multi-Agente",
            page_icon="🚢",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        self._aplicar_estilos_maritimos()
        self._renderizar_sidebar()

        # Renderizado del Banner del encabezado principal
        st.markdown(
            """
            <div class="deporca-header">
                <div>
                    <div class="deporca-title">
                        🚢 DEPORCA — Sistema de Gestión Portuaria y Carga Marítima
                    </div>
                    <div class="deporca-subtitle">
                        Asistente Inteligente Multi-Agente para Operaciones,
                        Tarifas y Normativa Portuaria
                    </div>
                </div>
                <div style="font-size: 32px;">⚓</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Inicialización perezosa del estado de mensajes en session_state
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        "¡Bienvenido a **DEPORCA**! Soy tu asistente de operaciones "
                        "portuarias y carga marítima. ¿En qué consulta puedo colaborarte hoy?"
                    ),
                    "avatar": "⚓",
                }
            ]

        # Re-renderizado del historial guardado en la sesión
        for msg in st.session_state.messages:
            avatar = msg.get("avatar", "👤" if msg["role"] == "user" else "⚓")
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # Captura y procesamiento en vivo del prompt del usuario
        if pregunta_usuario := st.chat_input(
            "Consulta sobre tarifas, depósitos de carga o auditorías..."
        ):
            # 1. Registrar y mostrar la entrada del usuario
            st.session_state.messages.append(
                {"role": "user", "content": pregunta_usuario, "avatar": "📦"}
            )
            with st.chat_message("user", avatar="📦"):
                st.markdown(pregunta_usuario)

            # 2. Ejecutar la inferencia del Grafo y presentar la respuesta
            with st.chat_message("assistant", avatar="⚓"):
                with st.spinner("🚢 Procesando consulta con la flota de agentes..."):
                    try:
                        # Se construye la estructura explícita del estado inicial del grafo
                        estado_inicial: EstadoGrafo = {
                            "pregunta_usuario": pregunta_usuario,
                            "agentes": self.agentes,
                            "payload_orquestador": None,
                            "respuesta_auditor": None,
                            "respuesta_financiero": None,
                            "respuesta_bot": None,
                            "respuesta_final": "",
                        }

                        # Invocación sincrónica del grafo LangGraph
                        resultado: Dict[str, Any] = self.app.invoke(estado_inicial)
                        respuesta_texto: str = resultado.get(
                            "respuesta_final",
                            "El sistema no generó una respuesta adecuada.",
                        )

                        st.markdown(respuesta_texto)
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": respuesta_texto,
                                "avatar": "⚓",
                            }
                        )

                    except Exception as error:
                        # Manejo seguro para prevenir cierres inesperados de la app
                        msg_error = f"❌ Ocurrió un error en el procesador: {str(error)}"
                        st.error(msg_error)
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": msg_error,
                                "avatar": "⚠️",
                            }
                        )