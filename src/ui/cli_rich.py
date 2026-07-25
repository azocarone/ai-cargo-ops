"""Módulo de Interfaz de Línea de Comandos (CLI) para DEPORCA.

Proporciona una consola interactiva (REPL) estilizada mediante la librería `rich`,
diseñada para gestionar la interacción en tiempo real entre el usuario y la
flota multi-agente de gestión portuaria y logística de carga marítima.
"""

from typing import Any, Dict, Final, Set

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# Extracción de literales a constantes inmutables para mejorar mantenibilidad
COMANDOS_SALIDA: Final[Set[str]] = {"salir", "exit", "quit"}
COMANDOS_ESTADO: Final[Set[str]] = {"agentes", "flota", "status"}


class InterfazCLI:
    """Gestiona el bucle de interacción de consola (REPL) estilizado con Rich.

    Esta clase abstrae la representación visual del flujo de orquestación
    multi-agente, transformando las entradas del usuario en estados ejecutables
    para el grafo y renderizando las respuestas formateadas.

    Attributes:
        app (Any): Instancia compilada del grafo de orquestación (LangGraph).
        agentes (Dict[str, Any]): Mapa de agentes activos en el sistema.
        console (Console): Instancia de renderizado para terminal de Rich.
    """

    def __init__(self, app_grafo: Any, agentes: Dict[str, Any]) -> None:
        """Inicializa la CLI con sus dependencias de orquestación.

        Args:
            app_grafo: Instancia compilada del grafo ejecutable (LangGraph).
            agentes: Diccionario con la jerarquía y referencias de agentes activos.
        """
        self.app = app_grafo
        self.agentes = agentes
        self.console = Console()

    def _mostrar_banner(self) -> None:
        """Renderiza el banner de bienvenida e información institucional."""
        banner_art = """
 ╔═════════════════════════════════════════════════════════════════════════════════════╗
 ║  🚢  D E P O R C A  —  S I S T E M A   M U L T I - A G E N T E   P O R T U A R I O  ║
 ╚═════════════════════════════════════════════════════════════════════════════════════╝
        """
        self.console.print(Text(banner_art, style="bold cyan"))

        info_panel = Panel(
            Text.from_markup(
                "[bold gold1]Almacenes y Depósitos Integrales Portuarios, C.A.[/bold gold1]\n"
                "[italic cyan]Asistente Inteligente de Gestión de Carga Marítima, Tarifas y Normativa[/italic cyan]\n\n"
                "[dim]• Escribe [bold white]'salir'[/bold white], [bold white]'exit'[/bold white] o [bold white]'quit'[/bold white] para terminar.\n"
                "• Escribe [bold white]'agentes'[/bold white] o [bold white]'flota'[/bold white] para consultar el estado del equipo.[/dim]"
            ),
            title="[bold white]⚓ Control Operativo de Puerto[/bold white]",
            border_style="bold blue",
            padding=(0, 2),
        )
        self.console.print(info_panel)
        self.console.print()

    def _mostrar_flota_agentes(self) -> None:
        """Despliega una tabla con el estado y rol de cada agente de la flota."""
        table = Table(
            title="🚢 Flota de Agentes Multi-Agente Activa",
            header_style="bold gold1",
            border_style="blue",
            expand=True,
        )

        table.add_column("Ícono", justify="center", style="bold cyan", width=6)
        table.add_column("Agente", style="bold white", width=22)
        table.add_column("Especialidad / Rol", style="italic cyan")
        table.add_column("Estado", justify="center", style="bold green", width=10)

        table.add_row("🎯", "Orquestador", "Clasificación de intenciones y enrutamiento operacional", "ACTIVO 🟢")
        table.add_row("📊", "Financiero", "Cálculo de tarifas, fletes, impuestos y liquidaciones", "ACTIVO 🟢")
        table.add_row("🔍", "Auditor RAG", "Verificación de normativa aduanera y depósitos", "ACTIVO 🟢")
        table.add_row("🤖", "Asistente General", "Soporte operativo y consultas portuarias", "ACTIVO 🟢")

        self.console.print(table)
        self.console.print()

    def iniciar(self) -> None:
        """Inicia el bucle principal de interacción en consola (REPL).

        Mantiene la sesión activa escuchando consultas, procesando comandos
        de control y derivando la ejecución al motor de orquestación.
        """
        self.console.clear()
        self._mostrar_banner()

        while True:
            try:
                pregunta: str = Prompt.ask(
                    "[bold cyan]⚓ [DEPORCA Cargo Input][/bold cyan]"
                ).strip()

                pregunta_normalizada = pregunta.lower()

                # Evaluación de comandos mediante conjuntos O(1)
                if pregunta_normalizada in COMANDOS_SALIDA:
                    self.console.print(
                        "\n[bold gold1]⚓ Operación finalizada. ¡Buen viaje y mares calmos![/bold gold1]\n"
                    )
                    break

                if pregunta_normalizada in COMANDOS_ESTADO:
                    self._mostrar_flota_agentes()
                    continue

                # Guarda de validación previa
                if not pregunta:
                    self.console.print(
                        "[bold red]⚠️ Por favor, ingresa una pregunta o consulta válida.[/bold red]\n"
                    )
                    continue

                # Definición limpia del estado inicial que requiere el grafo de LangGraph
                estado_inicial: Dict[str, Any] = {
                    "pregunta_usuario": pregunta,
                    "agentes": self.agentes,
                    "payload_orquestador": None,
                    "respuesta_auditor": None,
                    "respuesta_financiero": None,
                    "respuesta_bot": None,
                    "respuesta_final": "",
                }

                self._procesar_y_mostrar(estado_inicial)

            except KeyboardInterrupt:
                # Interrupción limpia (Ctrl+C) evitando trazas de error innecesarias
                self.console.print(
                    "\n\n[bold gold1]⚓ Interrupción detectada. ¡Hasta luego![/bold gold1]\n"
                )
                break

    def _procesar_y_mostrar(self, estado_inicial: Dict[str, Any]) -> None:
        """Ejecuta la invocación del grafo de orquestación y renderiza la respuesta.

        Args:
            estado_inicial: Diccionario de estado que alimentará el flujo
                del grafo ejecutable en LangGraph.
        """
        self.console.print()

        # Feedback visual mediante spinner durante la ejecución síncrona/asíncrona
        with self.console.status(
            "[bold cyan]🚢 Procesando embarque de consulta con la flota de agentes...[/bold cyan]",
            spinner="dots",
        ):
            try:
                resultado: Dict[str, Any] = self.app.invoke(estado_inicial)
                respuesta: str = resultado.get(
                    "respuesta_final",
                    "El sistema no generó una respuesta adecuada.",
                )

                panel_respuesta = Panel(
                    respuesta,
                    title="[bold gold1]📦 RESUMEN Y DESPACHO DE CONSULTA[/bold gold1]",
                    subtitle="[dim cyan]DEPORCA Multi-Agent Engine[/dim cyan]",
                    border_style="bright_blue",
                    padding=(1, 2),
                )
                self.console.print(panel_respuesta)
                self.console.print(Rule(style="blue"))
                self.console.print()

            except Exception as error:
                # Aislamiento de excepciones para garantizar la estabilidad del REPL
                self.console.print(
                    Panel(
                        f"[bold red]❌ Fallo en la travesía del orquestador:[/bold red]\n{error}",
                        title="[bold red]Error de Procesamiento[/bold red]",
                        border_style="red",
                    )
                )