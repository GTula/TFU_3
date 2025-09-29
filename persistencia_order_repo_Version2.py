from models.order import Order

orders_db = {}

def get_all_orders():
    return list(orders_db.values())

def get_order(order_id: int):
    return orders_db.get(order_id)

def add_order(order: Order):
    orders_db[order.id] = order
    return order

def update_order(order_id: int, order: Order):
    orders_db[order_id] = order
    return order

def delete_order(order_id: int):
    return orders_db.pop(order_id, None)