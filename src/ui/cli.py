"""Módulo de Interfaz de Línea de Comandos (CLI) para el sistema DEPORCA.

Este módulo encapsula toda la interacción por consola con el usuario (entrada de
datos, validaciones de texto y salida de respuestas), desacoplándola por
completo de la lógica de orquestación principal.
"""

from typing import Any, Dict


class InterfazCLI:
    """Gestiona el bucle de interacción de consola (REPL) con el usuario."""

    def __init__(self, app_grafo: Any, agentes: Dict[str, Any]) -> None:
        """Inicializa la CLI con el grafo compilado y el mapa de agentes.

        Args:
            app_grafo: Instancia del grafo de LangGraph compilado.
            agentes: Diccionario con la jerarquía de agentes instanciados.
        """
        self.app = app_grafo
        self.agentes = agentes

    def iniciar(self) -> None:
        """Inicia el bucle principal de conversación en consola."""
        print("===========================================")
        print("=== Sistema Multi-Agente DEPORCA Activo ===")
        print("===========================================")
        print("Escribe 'salir', 'exit' o 'quit' para terminar.\n")

        while True:
            pregunta: str = input("Ingresa tu consulta: ").strip()

            # Evaluación de la condición de salida
            if pregunta.lower() in ("salir", "exit", "quit"):
                print("\n¡Hasta luego!")
                break

            # Validar que no se envíe un texto vacío
            if not pregunta:
                print("Por favor, ingresa una pregunta válida.\n")
                continue

            # Construcción del payload de estado inicial
            estado_inicial: Dict[str, Any] = {
                "pregunta_usuario": pregunta,
                "agentes": self.agentes,
                "payload_orquestador": None,
                "respuesta_auditor": None,
                "respuesta_financiero": None,
                "respuesta_bot": None,
                "respuesta_final": "",
            }

            # Procesamiento mediante el grafo
            self._procesar_y_mostrar(estado_inicial)

    def _procesar_y_mostrar(self, estado_inicial: Dict[str, Any]) -> None:
        """Invoca el grafo de agentes y formatea la respuesta devuelta.

        Args:
            estado_inicial: Estado base requerido por LangGraph para iniciar.
        """
        try:
            resultado: Dict[str, Any] = self.app.invoke(estado_inicial)
            respuesta: str = resultado.get(
                "respuesta_final", 
                "El sistema no generó una respuesta adecuada."
            )

            print("\n--- RESUMEN FINAL ---")
            print(respuesta)
            print("\n" + "=" * 40 + "\n")

        except Exception as error:
            print(f"\n[ERROR] Ocurrió un fallo durante la ejecución: {error}\n")