from persistencia.client_repo import (
    get_all_clients, get_client, add_client, update_client, delete_client
)
from models.client import Client

def listar_clientes():
    return get_all_clients()

def obtener_cliente(client_id: int):
    return get_client(client_id)

def crear_cliente(client: Client):
    return add_client(client)

def actualizar_cliente(client_id: int, client: Client):
    return update_client(client_id, client)

def eliminar_cliente(client_id: int):
    return delete_client(client_id)