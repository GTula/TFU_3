from persistencia.client_repo import listar_clientes, obtener_cliente, crear_cliente

def obtener_todos_clientes():
    return listar_clientes()

def obtener_un_cliente(client_id):
    return obtener_cliente(client_id)

def agregar_cliente(client):
    if "@" not in client["email"]:
        raise ValueError("El email no es válido")
    return crear_cliente(client)