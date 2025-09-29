from persistencia.product_repo import listar_productos, obtener_producto, crear_producto

def obtener_todos_productos():
    return listar_productos()

def obtener_un_producto(product_id):
    return obtener_producto(product_id)

def agregar_producto(product):
    if product["stock"] < 0:
        raise ValueError("El stock no puede ser negativo")
    return crear_producto(product)