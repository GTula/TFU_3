from persistencia.order_repo import listar_ordenes, obtener_orden, crear_orden

def obtener_todas_ordenes():
    return listar_ordenes()

def obtener_una_orden(order_id):
    return obtener_orden(order_id)

def agregar_orden(order):
    if not order.get("items"):
        raise ValueError("La orden debe tener items")
    resultado = crear_orden(order)
    if not resultado:
        raise ValueError("Orden inválida: cliente o productos incorrectos")
    return resultado