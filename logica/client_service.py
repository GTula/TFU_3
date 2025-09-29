from models.client import Client
from persistencia.client_repo import (
    get_all_clients, get_client, add_client, update_client, delete_client
)
from sqlalchemy.orm import Session

def listar_clientes(db: Session):
    return get_all_clients(db)

def obtener_cliente(db: Session, client_id: int):
    return get_client(db, client_id)

def crear_cliente(db: Session, client_data: dict):
    client = Client(**client_data)
    return add_client(db, client)

def actualizar_cliente(db: Session, client_id: int, data: dict):
    return update_client(db, client_id, data)

def eliminar_cliente(db: Session, client_id: int):
    return delete_client(db, client_id)