from models.order import Order
from persistencia.order_repo import (
    get_all_orders, get_order, add_order, delete_order
)
from sqlalchemy.orm import Session

def listar_ordenes(db: Session):
    return get_all_orders(db)

def obtener_orden(db: Session, order_id: int):
    return get_order(db, order_id)

def crear_orden(db: Session, order_data: dict):
    items = order_data.pop("items")
    order = Order(**order_data)
    return add_order(db, order, items)

def eliminar_orden(db: Session, order_id: int):
    return delete_order(db, order_id)