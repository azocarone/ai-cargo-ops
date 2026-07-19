import json

preguntas_del_usuario = [
    "Hola, requiero exportar 3 contenedores en un mismo booking desde Valencia hacia el puerto. Además, uno de ellos tiene una factura con 5 ítems de clasificación arancelaria compleja. ¿Cuánto me costaría el agenciamiento, la DUA y el transporte? ¿Puedo pagar en bolívares?",
    "¿Qué documentos integran el 'Expediente Especial de Trazabilidad de Planta' en caso de una alerta antidrogas?",
    "¿Qué pasa si se agrieta un contenedor?",
    "¿Qué debe hacer el Agente de Aduanas si el funcionario del SENIAT tiene un criterio técnico con el que la empresa no está de acuerdo?"
    "¿Bajo qué jurisdicción aduanera opera exclusivamente DEPORCA?",
    "¿Cuánto me sale el flete para mañana? Y otra cosa, ¿cómo hago con la inspección del precinto?",
    "¿Bajo qué jurisdicción aduanera opera exclusivamente DEPORCA?",
    "¿Cuál es el costo del agenciamiento aduanal para el primer contenedor de un embarque?",
    "Hola, buenas tardes, necesito ayuda por favor.",
    "Hola, cuanto sale un flete.",
    "Hola"
]

def test_agente(agente, lista_preguntas=preguntas_del_usuario):
    """
    Procesa una lista de mensajes a través de una función de agente 
    y retorna todos los resultados agrupados en una lista.
    """
    
    respuesta_final = agente.consultar(lista_preguntas[3])
    
    #print(json.dumps(respuesta_final, indent=4, ensure_ascii=False))
    print(respuesta_final.model_dump_json(indent=4))