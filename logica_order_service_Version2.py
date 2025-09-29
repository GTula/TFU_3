from persistencia.order_repo import (
    get_all_orders, get_order, add_order, update_order, delete_order
)
from models.order import Order

def listar_ordenes():
    return get_all_orders()

def obtener_orden(order_id: int):
    return get_order(order_id)

def crear_orden(order: Order):
    return add_order(order)

def actualizar_orden(order_id: int, order: Order):
    return update_order(order_id, order)

def eliminar_orden(order_id: int):
    return delete_order(order_id)