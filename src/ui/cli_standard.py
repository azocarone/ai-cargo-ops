"""Módulo de Interfaz de Línea de Comandos (CLI) para el sistema DEPORCA.

Este módulo encapsula la capa de presentación por consola con el usuario
(captura de entrada, sanitización de datos y visualización de resultados),
desacoplándola por completo de la lógica de orquestación y compilación del grafo.

Cumple con el patrón REPL (Read-Eval-Print Loop) y aplica principios de 
inyección de dependencias para facilitar su mantenimiento y modularidad.
"""

from typing import Any, Dict, Final, Tuple, TypedDict


class EstadoGrafo(TypedDict, total=False):
    """Estructura del estado global transferido a través de los nodos del grafo."""

    pregunta_usuario: str
    agentes: Dict[str, Any]
    payload_orquestador: Any
    respuesta_auditor: Any
    respuesta_financiero: Any
    respuesta_bot: Any
    respuesta_final: str


class InterfazCLI:
    """Gestiona el bucle de interacción de consola (REPL) con el usuario.
    
    Attributes:
        COMANDOS_SALIDA: Tupla inmutable con las palabras clave reconocidas 
                         para finalizar la sesión de interacción.
    """

    COMANDOS_SALIDA: Final[Tuple[str, ...]] = ("salir", "exit", "quit")

    def __init__(self, app_grafo: Any, agentes: Dict[str, Any]) -> None:
        """Inicializa la CLI inyectando las dependencias necesarias.

        Args:
            app_grafo: Instancia del grafo compilado (ej. Runnable o CompiledStateGraph
                de LangGraph) expuesta para invocar la ejecución.
            agentes: Mapa de agentes instanciados clave-valor requeridos por la
                infraestructura.
        """
        self.app = app_grafo
        self.agentes = agentes

    def iniciar(self) -> None:
        """Inicia el bucle principal de conversación en consola (Read-Eval-Print Loop).
        
        Mantiene la ejecución continua hasta que el usuario introduzca una de las
        palabras clave declaradas en `COMANDOS_SALIDA`. Sanitiza las entradas y 
        prepara la estructura de estado para el motor de ejecución.
        """
        print("===========================================")
        print("=== Sistema Multi-Agente DEPORCA Activo ===")
        print("===========================================")
        print("Escribe 'salir', 'exit' o 'quit' para terminar.\n")

        while True:
            # Captura y sanitización básica del texto ingresado por teclado
            pregunta: str = input("Ingresa tu consulta: ").strip()

            # Evaluación de la condición de detención antes de proceder con el procesamiento
            if pregunta.lower() in self.COMANDOS_SALIDA:
                print("\n¡Hasta luego!")
                break

            # Validación del lado de la UI: evita llamadas infructuosas al grafo si la entrada es vacía
            if not pregunta:
                print("Por favor, ingresa una pregunta válida.\n")
                continue

            # Construcción del estado inicial estandarizado conforme al esquema del grafo.
            # Este diccionario representa el snapshot de entrada para el motor multi-agente.
            estado_inicial: EstadoGrafo = {
                "pregunta_usuario": pregunta,
                "agentes": self.agentes,
                "payload_orquestador": None,
                "respuesta_auditor": None,
                "respuesta_financiero": None,
                "respuesta_bot": None,
                "respuesta_final": "",
            }

            # Delegación de la ejecución y despliegue del resultado
            self._procesar_y_mostrar(estado_inicial)

    def _procesar_y_mostrar(self, estado_inicial: EstadoGrafo) -> None:
        """Invoca el grafo de agentes y formatea la respuesta devuelta al usuario.

        Aplica una barrera de contención de errores en la capa de UI para garantizar 
        que fallos en nodos internos del grafo no detengan abruptamente el proceso REPL.

        Args:
            estado_inicial: Estado base tipado requerido por LangGraph para iniciar el flujo.
        """
        try:
            # Invocación sincrónica del grafo. 'resultado' contiene el estado acumulado final.
            resultado: Dict[str, Any] = self.app.invoke(estado_inicial)
            respuesta: str = resultado.get(
                "respuesta_final", 
                "El sistema no generó una respuesta adecuada."
            )

            print("\n--- RESUMEN FINAL ---")
            print(respuesta)
            print("\n" + "=" * 40 + "\n")

        except Exception as error:
            # Captura defensiva en la frontera de la interfaz para informar al usuario 
            # sin colapsar el hilo de la CLI.
            print(f"\n[ERROR] Ocurrió un fallo durante la ejecución: {error}\n")